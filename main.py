import uuid
import asyncio # Keep for async views if any, though /api/take will become sync
import logging
import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
# from app.utils.screenshot_taker import take_screenshot # Replaced by task
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Celery related imports
from celery_worker import celery_app # Import celery_app instance
from app.utils.screenshot_taker import process_screenshot_task # Import the task


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey_dev_fallback') # Prioritize env var

# --- App Configurations ---
# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://user:password@localhost/screenshotone_db' # Placeholder
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Screenshot output directory
app.config['SCREENSHOT_OUTPUT_DIR'] = os.environ.get('SCREENSHOT_OUTPUT_DIR', '/tmp/screenshots')
if not os.path.exists(app.config['SCREENSHOT_OUTPUT_DIR']):
    os.makedirs(app.config['SCREENSHOT_OUTPUT_DIR'], exist_ok=True)

# Celery Broker and Backend configuration (read by celery_app in celery_worker.py)
# These are not strictly needed here if celery_worker.py handles them, but good for clarity.
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

db = SQLAlchemy(app)

# Configure logging (ensure it's after app initialization)
# Using app.logger directly is fine for Flask's built-in logger.
# The setup in celery_worker.py configures celery_app.logger.
if not app.debug and not app.testing: # Avoid duplicate handlers in debug/test
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    if not app.logger.handlers:
        app.logger.addHandler(log_handler)
        app.logger.setLevel(logging.INFO)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for future hash algo
    api_key = db.Column(db.String(128), unique=True, nullable=False, index=True)
    usages = db.relationship('ApiUsage', backref='user', lazy=True, cascade="all, delete-orphan")

class ApiUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    # Default to the first day of the current month
    period_start_date = db.Column(db.Date, nullable=False, default=lambda: datetime.date.today().replace(day=1))
    count = db.Column(db.Integer, default=0)

# --- End Models ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Removed redundant 'if email in users_db:' check,
        # as database unique constraint handles this.
        password_hash = generate_password_hash(password)
        api_key = uuid.uuid4().hex
        password_hash = generate_password_hash(password)
        api_key = uuid.uuid4().hex
        
        new_user = User(email=email, password_hash=password_hash, api_key=api_key)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Create initial usage record for the current month
            today = datetime.date.today()
            current_month_start = today.replace(day=1)
            initial_usage = ApiUsage(user_id=new_user.id, period_start_date=current_month_start, count=0)
            db.session.add(initial_usage)
            db.session.commit()
            
            app.logger.info(f"New user registered: {email}")
            flash('Registration successful. Please sign in.')
            return redirect(url_for('signin_get'))
        except IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Registration failed for {email}: {e}")
            if 'user_email_key' in str(e.orig).lower() or 'user_email_key' in str(e.args[0]).lower(): # Check constraint name
                 flash('Email already exists.')
            elif 'user_api_key_key' in str(e.orig).lower() or 'user_api_key_key' in str(e.args[0]).lower(): # Check constraint name for api_key
                 flash('API key generation conflict. Please try again.') # Should be rare
            else:
                 flash('Registration failed due to a database error.')
            return redirect(url_for('signup'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Generic registration failed for {email}: {e}")
            flash('An unexpected error occurred during registration.')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

@app.route('/signin', methods=['GET'])
def signin_get():
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin_post():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['email'] = user.email
        app.logger.info(f"User logged in: {email}")
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('signin_get'))

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('signin_get'))

    user_email_from_session = session['email'] # Renamed to avoid conflict
    user = User.query.filter_by(email=user_email_from_session).first()

    if not user:
        flash('User not found. Please sign in again.')
        session.pop('email', None)
        return redirect(url_for('signin_get'))

    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    
    usage_record = ApiUsage.query.filter_by(
        user_id=user.id, 
        period_start_date=current_month_start
    ).first()
    
    usage_count = usage_record.count if usage_record else 0
    
    return render_template('dashboard.html', api_key=user.api_key, usage_count=usage_count)

@app.route('/signout')
def signout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/api/take', methods=['GET']) # Changed from async def to def
def api_take(): # Changed from async def to def
    url = request.args.get('url')
    access_key = request.args.get('access_key')
    request_id = uuid.uuid4().hex # For correlating logs

    if not url or not access_key:
        app.logger.warning(f"[Request {request_id}] API call failed: Missing parameters. IP: {request.remote_addr}")
        return jsonify({"error": "Missing or invalid parameters."}), 400

    user = User.query.filter_by(api_key=access_key).first()
    
    if not user:
        app.logger.warning(f"[Request {request_id}] API call failed: Invalid access key {access_key}. IP: {request.remote_addr}")
        return jsonify({"error": "Unauthorized or usage limit exceeded."}), 401 # Keep generic for security

    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    
    usage_record = ApiUsage.query.filter_by(
        user_id=user.id,
        period_start_date=current_month_start
    ).first()

    # Create usage record if it doesn't exist (e.g. first use in a new month)
    if not usage_record:
        usage_record = ApiUsage(user_id=user.id, period_start_date=current_month_start, count=0)
        db.session.add(usage_record)
        try:
            db.session.commit() # Commit new usage record before checking count
            app.logger.info(f"[Request {request_id}] Created initial usage record for user {user.email} for month {current_month_start.strftime('%Y-%m')}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"[Request {request_id}] Failed to create initial usage record for {user.email}. Error: {e}")
            return jsonify({"error": "Internal server error during usage record creation."}), 500


    if usage_record.count >= 100:
        app.logger.warning(f"[Request {request_id}] API call failed: Usage limit exceeded for user {user.email}. IP: {request.remote_addr}")
        return jsonify({"error": "Unauthorized or usage limit exceeded."}), 401

    app.logger.info(f"[Request {request_id}] API call attempt by {user.email} for URL: {url}. Queueing task.")
    
    # Queue the Celery task
    # Note: Usage increment is now handled by the Celery task itself upon successful screenshot.
    task = process_screenshot_task.delay(user_id=user.id, url=url, request_id=request_id)
    
    app.logger.info(f"[Request {request_id}] Task {task.id} queued for user {user.email}, URL: {url}")
    
    return jsonify({"message": "Screenshot request queued.", "task_id": task.id}), 202


@app.route('/api/status/<task_id>')
def task_status(task_id):
    task = celery_app.AsyncResult(task_id) # Use celery_app from celery_worker
    response_data = {"task_id": task_id, "status": task.state}
    
    if task.state == 'PENDING':
        # Nothing more to add
        pass
    elif task.state == 'SUCCESS':
        response_data['filename'] = task.result
        response_data['download_url'] = url_for('retrieve_screenshot', filename=task.result, _external=True)
    elif task.state == 'FAILURE':
        response_data['error'] = str(task.info) # task.info holds the exception
        # Could also log task.traceback here for more detailed server-side debugging
        app.logger.error(f"Task {task_id} failed. Error: {task.info}\nTraceback: {task.traceback}")
    # Other states could be 'STARTED', 'RETRY', 'REVOKED'
    
    return jsonify(response_data)

@app.route('/api/retrieve/<filename>')
def retrieve_screenshot(filename):
    app.logger.info(f"Attempting to retrieve screenshot: {filename}")
    # Security: Validate filename to prevent directory traversal if needed,
    # though send_from_directory should handle this reasonably well.
    # For example, ensure filename does not contain '..' or '/'
    if '..' in filename or filename.startswith('/'):
        app.logger.warning(f"Invalid filename requested for retrieval: {filename}")
        return jsonify({"error": "Invalid filename"}), 400
        
    try:
        return send_from_directory(
            app.config['SCREENSHOT_OUTPUT_DIR'], 
            filename, 
            as_attachment=True # Optional: forces download dialog
        )
    except FileNotFoundError:
        app.logger.error(f"Screenshot file not found: {filename}")
        return jsonify({"error": "File not found or processing not complete."}), 404

# Database initialization command (run once manually or via a script)
def init_db():
    with app.app_context():
        db.create_all()
    print("Database tables created (if they didn't exist).")

if __name__ == '__main__':
    # Consider making this a CLI command, e.g., using Flask-Click
    # For now, you can run this function from a Python shell:
    # from main import init_db # If you need to run init_db manually
    # with app.app_context(): init_db() # If you need to run init_db manually
    app.run(debug=True)
