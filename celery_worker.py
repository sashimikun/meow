from celery import Celery
import os

# Default to local Redis if REDIS_URL is not set
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    __name__, # Using a generic name as tasks might be defined elsewhere
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.utils.screenshot_taker'] # Path to the module where tasks are defined
)

# Optional: Update Celery configuration with Flask app config if needed by tasks
# celery_app.conf.update(flask_app.config) # This would require flask_app to be imported

# Import Flask app instance
# This import should be structured to avoid circular dependencies if main.py also imports celery_app.
# One common way is to ensure main.py's Flask app object is created before celery_worker.py is fully processed
# or by having a central app factory. For this setup, we'll assume direct import is manageable.
# If 'main.app' causes issues, we might need to restructure Flask app creation (e.g. app_factory).
try:
    from main import app as flask_app # Assuming flask_app is the name in main.py
except ImportError:
    # This fallback is for when celery_worker.py might be run directly as a script
    # and main.py isn't in the Python path in the same way, or for tests.
    # A proper app factory pattern would be better for complex scenarios.
    flask_app = None 

# Update Celery configuration with Flask app config if needed by tasks and flask_app is available
if flask_app:
    celery_app.conf.update(flask_app.config)

class ContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        if flask_app:
            with flask_app.app_context():
                return self.run(*args, **kwargs)
        else:
            # This means flask_app wasn't available. Tasks might fail if they need app context.
            # Consider logging a warning or raising an error if app context is critical.
            print("Warning: Celery task running without Flask app context.")
            return self.run(*args, **kwargs)

# Set the default Task class for celery_app
celery_app.Task = ContextTask

if __name__ == '__main__':
    # This allows running the worker directly using: python celery_worker.py worker -l info
    # Ensure that main.py and other necessary modules are in PYTHONPATH
    celery_app.worker_main()
