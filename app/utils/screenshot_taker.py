import asyncio
import os
import uuid
import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Import Celery app instance and models
# Assuming celery_app is in celery_worker.py and flask_app (for config) is in main.py
from celery_worker import celery_app, flask_app
from main import db, User, ApiUsage # db and models are needed for database operations in task

# Ensure SCREENSHOT_OUTPUT_DIR exists (it's configured on flask_app)
# This check will run when the module is loaded by the worker.
# It's better if the main app ensures this directory on startup.
if flask_app:
    SCREENSHOT_DIR = flask_app.config.get('SCREENSHOT_OUTPUT_DIR', '/tmp/screenshots')
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
else:
    # Fallback if flask_app is not available during module load (e.g. some test scenarios)
    # Tasks running without flask_app context might not work correctly if they rely on app.config
    SCREENSHOT_DIR = '/tmp/screenshots'
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    print(f"Warning: flask_app not available during module load. SCREENSHOT_DIR set to {SCREENSHOT_DIR}")


@celery_app.task(bind=True) # base=ContextTask is implicitly set by celery_app.Task = ContextTask
def process_screenshot_task(self, user_id: int, url: str, request_id: str | None = None):
    """
    Celery task to take a screenshot, save it to a file, and update usage.
    Requires Flask app context for database operations and config.
    """
    log_prefix = f"[Task {self.request.id} | Request {request_id}]" if request_id else f"[Task {self.request.id}]"
    
    if not flask_app: # Should not happen if ContextTask is working correctly
        celery_app.logger.error(f"{log_prefix} Flask app context not available. Cannot proceed.")
        raise Exception("Flask app context not available for task execution.")

    celery_app.logger.info(f"{log_prefix} Starting screenshot for user {user_id} and URL: {url}")

    # --- Database: Fetch User and Check/Update Usage ---
    # This part requires app_context, which ContextTask should provide.
    user = User.query.get(user_id)
    if not user:
        celery_app.logger.error(f"{log_prefix} User with ID {user_id} not found.")
        raise ValueError(f"User with ID {user_id} not found.")

    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    
    usage_record = ApiUsage.query.filter_by(
        user_id=user.id,
        period_start_date=current_month_start
    ).first()

    if not usage_record:
        celery_app.logger.info(f"{log_prefix} No usage record for {user.email} for current month. Creating one.")
        usage_record = ApiUsage(user_id=user.id, period_start_date=current_month_start, count=0)
        db.session.add(usage_record)
        # Commit immediately or after screenshot? Let's commit after successful screenshot.

    if usage_record.count >= 100:
        celery_app.logger.warning(f"{log_prefix} Usage limit already reached for user {user.email}. This check should ideally be before queuing.")
        # This task might have been queued before a final check, or usage incremented by another parallel task.
        raise Exception(f"Usage limit exceeded for user {user.email}.")

    # --- Screenshot Logic (adapted from take_screenshot) ---
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    screenshot_bytes = None
    try:
        async def take_screenshot_async():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                img_bytes = await page.screenshot(full_page=True, path=filepath) # Save directly to path
                await browser.close()
                return img_bytes # Though not strictly needed if saved to path
        
        screenshot_bytes = loop.run_until_complete(take_screenshot_async())
        celery_app.logger.info(f"{log_prefix} Screenshot saved to {filepath}")

    except PlaywrightTimeoutError:
        celery_app.logger.error(f"{log_prefix} Timeout error for URL: {url}")
        raise # Re-raise to mark task as failed
    except Exception as e:
        celery_app.logger.error(f"{log_prefix} Screenshot failed for URL {url}: {e}")
        raise # Re-raise to mark task as failed
    finally:
        loop.close()

    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
         celery_app.logger.error(f"{log_prefix} Screenshot file not created or empty at {filepath} despite no direct error.")
         raise Exception("Screenshot file not created or empty.")

    # --- Update Usage (if screenshot was successful) ---
    try:
        usage_record.count += 1
        db.session.commit()
        celery_app.logger.info(f"{log_prefix} Usage count for user {user.email} incremented to {usage_record.count}.")
    except Exception as e:
        db.session.rollback()
        celery_app.logger.error(f"{log_prefix} Failed to update usage count for {user.email}: {e}. Screenshot at {filepath} might not be billed.")
        # Depending on policy, might want to delete the screenshot file if usage isn't recorded.
        # For now, we'll return the filename, but log the billing error.
        # Re-raising the exception here would mark the task as failed despite successful screenshot.
        # This is a business logic decision. For now, let's assume screenshot is more important.
        # raise Exception(f"Failed to update usage: {e}") # Uncomment to mark task as failed on db error

    return filename # Return just the filename, not the full path

# Original take_screenshot function is no longer needed as its logic is moved to the Celery task.
# If it were needed for non-Celery synchronous use, it would need to be refactored
# to not conflict (e.g., by also saving to a file or returning bytes directly).
# For this PR, we assume it's fully replaced by the async task model.
# async def take_screenshot(url: str) -> bytes | None: ... (original removed)
