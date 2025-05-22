import uuid
import asyncio
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.screenshot_taker import take_screenshot

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a real secret key in production

# Configure logging
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)

users_db = {}
usage_db = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users_db:
            flash('Email already exists')
            return redirect(url_for('signup'))

        password_hash = generate_password_hash(password)
        api_key = uuid.uuid4().hex
        users_db[email] = {'password_hash': password_hash, 'api_key': api_key}
        usage_db[email] = 0
        app.logger.info(f"New user registered: {email}")
        return redirect(url_for('signin'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET'])
def signin_get():
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin_post():
    email = request.form['email']
    password = request.form['password']

    user = users_db.get(email)
    if user and check_password_hash(user['password_hash'], password):
        session['email'] = email
        app.logger.info(f"User logged in: {email}")
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('signin_get'))

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('signin_get'))

    email = session['email']
    api_key = users_db[email]['api_key']
    usage_count = usage_db[email]
    return render_template('dashboard.html', api_key=api_key, usage_count=usage_count)

@app.route('/signout')
def signout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/api/take', methods=['GET'])
async def api_take():
    url = request.args.get('url')
    access_key = request.args.get('access_key')

    if not url or not access_key:
        app.logger.warning(f"API call failed: Missing parameters. IP: {request.remote_addr}")
        return jsonify({"error": "Missing or invalid parameters."}), 400

    user_email = None
    for email_iter, user_data in users_db.items():
        if user_data['api_key'] == access_key:
            user_email = email_iter
            break
    
    if not user_email:
        app.logger.warning(f"API call failed: Invalid access key {access_key}. IP: {request.remote_addr}")
        return jsonify({"error": "Unauthorized or usage limit exceeded."}), 401

    if usage_db.get(user_email, 0) >= 100:
        app.logger.warning(f"API call failed: Usage limit exceeded for user {user_email}. IP: {request.remote_addr}")
        return jsonify({"error": "Unauthorized or usage limit exceeded."}), 401

    app.logger.info(f"API call attempt by {user_email} for URL: {url}")

    try:
        screenshot_bytes = await take_screenshot(url)
        if screenshot_bytes is None:
            app.logger.error(f"API call failed: Screenshot timeout for URL {url}. User: {user_email}")
            return jsonify({"error": "Screenshot generation timed out."}), 408
    except Exception as e:
        app.logger.error(f"API call failed: Internal server error during screenshot for {url}. User: {user_email}. Error: {e}")
        return jsonify({"error": "Internal server error."}), 500

    usage_db[user_email] += 1
    app.logger.info(f"Screenshot successful for {url} by {user_email}")
    response = make_response(screenshot_bytes)
    response.headers['Content-Type'] = 'image/png'
    return response, 200

if __name__ == '__main__':
    app.run(debug=True)
