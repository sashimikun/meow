# Screenshot ONE - MVP: Manual Testing Checklist (Post-Refactor)

This checklist reflects the application architecture using PostgreSQL, Celery, and Docker.

## Prerequisites & Setup

- **1. Install Docker and Docker Compose:**
  - Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
  - Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/) (often included with Docker Desktop).
- **2. Clone the Repository.**
- **3. Configure Environment (`.env` file):**
  - [ ] Create a `.env` file in the project root.
  - [ ] Populate it with necessary variables (refer to `README.md` "Running with Docker Compose" section for required variables like `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`).
- **4. Build and Run Services:**
  - [ ] Open a terminal in the project root and run: `docker-compose up --build -d`.
  - [ ] Verify all services (`db`, `redis`, `web`, `worker`) are running: `docker-compose ps`.
- **5. Initialize the Database (First Time Only):**
  - [ ] After services are up, run: `docker-compose exec web python -c "from main import init_db; init_db()"`.
  - [ ] Expected: "Database tables created (if they didn't exist)."
- **6. Tools:**
  - A web browser.
  - A tool for API requests (e.g., Postman, curl).

## Epic 1: User Onboarding & Management (Database Persistence)

### 1.1. Landing Page
- [ ] **Test:** Open the root URL of the web service (e.g., `http://localhost:8000/` if using default Docker Compose port).
- [ ] **Expected:** See "The Screenshot API for Developers" headline, description, and "Sign Up for Free" button.

### 1.2. User Signup
- [ ] **Test:** Click "Sign Up for Free" or navigate to `/signup`.
- [ ] **Expected:** Signup form appears.
- [ ] **Test:** Enter a new email (e.g., `persistentuser1@example.com`) and password. Click "Sign Up".
- [ ] **Expected:** Redirected to `/signin`. Server logs (via `docker-compose logs -f web`) show "New user registered...".
- [ ] **Test (Optional DB Check):** `docker-compose exec db psql -U youruser -d yourdb` (replace with `.env` values) then `SELECT * FROM "user" WHERE email='persistentuser1@example.com';`.
- [ ] **Expected:** User record exists. An initial `ApiUsage` record for the current month with count 0 should also exist for this user.
- [ ] **Test:** Try signing up with the *same* email (`persistentuser1@example.com`) again.
- [ ] **Expected:** Error message "Email already exists". Redirected back to `/signup`.

### 1.3. User Signin
- [ ] **Test:** Navigate to `/signin`.
- [ ] **Expected:** Signin form appears.
- [ ] **Test:** Enter valid credentials for `persistentuser1@example.com`. Click "Sign In".
- [ ] **Expected:** Redirected to `/dashboard`. Server logs show "User logged in...".
- [ ] **Test:** Enter invalid email or password.
- [ ] **Expected:** Error message "Invalid credentials". Redirected back to `/signin`.

### 1.4. Dashboard
- [ ] **Test:** After login, view the `/dashboard`.
- [ ] **Expected:**
    - Correct API key for `persistentuser1@example.com` displayed.
    - "Monthly Usage: 0 / 100 screenshots" (for a new user).
    - API usage instructions: `GET /api/take?url=<URL_TO_CAPTURE>&access_key=<YOUR_API_KEY>`. (Note: The actual API interaction is now async, this instruction might need a footnote about checking status).
- [ ] **Test:** Access `/dashboard` without being logged in (new browser session or after clearing cookies).
- [ ] **Expected:** Redirected to `/signin`.

### 1.5. User Signout
- [ ] **Test:** On the dashboard, click "Sign Out".
- [ ] **Expected:** Redirected to landing page. Session cleared.
- [ ] **Test:** Access `/dashboard` again.
- [ ] **Expected:** Redirected to `/signin`.

### 1.6. Data Persistence Test
- [ ] **Test:** With `persistentuser1@example.com` created:
    1. Stop the services: `docker-compose down`.
    2. Restart services: `docker-compose up -d` (no `--build` needed unless code changed).
    3. Navigate to `/signin` and log in with `persistentuser1@example.com`'s credentials.
- [ ] **Expected:** Login successful. Dashboard shows correct API key and usage count (which should still be 0 if no API calls were made). This verifies user data persists in the `postgres_data` volume.

## Epic 2: Core Screenshot API Usage (Asynchronous Flow)

**Setup:**
- Ensure you have a valid `access_key` from the dashboard of a registered user (e.g., `persistentuser1@example.com`).
- Choose test URLs (e.g., `https://example.com`, `https://playwright.dev`).
- Have a way to monitor Celery worker logs: `docker-compose logs -f worker`.
- Have a way to monitor web service logs: `docker-compose logs -f web`.

### 2.1. Successful Screenshot Request Flow
- **Step 1: Request Screenshot (`GET /api/take`)**
  - [ ] **Test:** Make GET request: `/api/take?url=https://example.com&access_key=YOUR_VALID_ACCESS_KEY`
  - [ ] **Expected:**
      - HTTP Status Code: `202 Accepted`.
      - Response body: `{"message": "Screenshot request queued.", "task_id": "SOME_TASK_ID"}`.
      - Web server log shows "API call attempt..." and "Task SOME_TASK_ID queued...".
      - Celery worker log shows the task received and starting.
  - [ ] **Action:** Note the `SOME_TASK_ID`.

- **Step 2: Check Task Status (`GET /api/status/<task_id>`)**
  - [ ] **Test:** Poll `GET /api/status/SOME_TASK_ID` (replace `SOME_TASK_ID` with actual ID).
  - [ ] **Expected (Initially):** `{"task_id": "SOME_TASK_ID", "status": "PENDING"}` or `{"status": "STARTED"}`.
  - [ ] **Test:** Continue polling until status changes.
  - [ ] **Expected (On Success):** `{"task_id": "SOME_TASK_ID", "status": "SUCCESS", "filename": "SOME_FILENAME.png", "download_url": "/api/retrieve/SOME_FILENAME.png"}` (The download URL might be absolute depending on `url_for` usage).
  - [ ] **Action:** Note `SOME_FILENAME.png`. Celery worker log should show task success and database update for usage.

- **Step 3: Retrieve Screenshot (`GET /api/retrieve/<filename>`)**
  - [ ] **Test:** Make GET request: `/api/retrieve/SOME_FILENAME.png` (replace `SOME_FILENAME.png`).
  - [ ] **Expected:**
      - HTTP Status Code: `200 OK`.
      - `Content-Type`: `image/png`.
      - Response body is a valid PNG image of `https://example.com`.
  - [ ] **Test:** Refresh dashboard for the user.
  - [ ] **Expected:** Usage count increments by 1 (e.g., "1 / 100 screenshots").
  - [ ] **Test (Optional DB Check):** Check `ApiUsage` table for the user; count should be 1.

### 2.2. API Request Errors (Direct Synchronous Errors from `/api/take`)
- **Missing Parameters:**
  - [ ] **Test:** `GET /api/take?access_key=YOUR_VALID_ACCESS_KEY` (missing `url`).
  - [ ] **Expected:** Status `400 Bad Request`. Response: `{"error": "Missing or invalid parameters."}`. Web log shows warning.
- **Invalid API Key:**
  - [ ] **Test:** `GET /api/take?url=https://example.com&access_key=INVALID_KEY_123`.
  - [ ] **Expected:** Status `401 Unauthorized`. Response: `{"error": "Unauthorized or usage limit exceeded."}`. Web log shows warning.

### 2.3. Task Failure (Asynchronous Errors, check via `/api/status`)
- **Screenshot Timeout / Invalid URL for Screenshotting:**
  - [ ] **Test:** Request screenshot for a known slow/problematic URL (e.g., `http://thissitedoesnotexistandwilltimeout.com`) via `/api/take`. Note the `task_id`.
  - [ ] **Test:** Poll `/api/status/<task_id>`.
  - [ ] **Expected:**
      - Status eventually becomes `FAILURE`.
      - Response: `{"task_id": "task_id", "status": "FAILURE", "error": "description of timeout or screenshot error"}`.
      - Celery worker log shows error details (e.g., "Timeout error for URL..." or "Screenshot failed...").
  - [ ] **Test:** Refresh dashboard for the user.
  - [ ] **Expected:** Usage count should NOT have incremented.

### 2.4. Usage Limit Exceeded
- [ ] **Test Setup:** Manually update a user's `ApiUsage` count to 99 or 100 in the database for the current month, or perform 99-100 successful screenshot operations.
- **With Usage at 99 (before limit is hit):**
  - [ ] **Test:** Make one more successful screenshot request (request, status, retrieve).
  - [ ] **Expected:** Screenshot successful, usage on dashboard becomes 100.
- **With Usage at 100 (limit is hit):**
  - [ ] **Test:** Make another call to `/api/take?url=https://example.com&access_key=USER_AT_LIMIT_KEY`.
  - [ ] **Expected (Direct Error):**
      - HTTP Status Code: `401 Unauthorized`.
      - Response body: `{"error": "Unauthorized or usage limit exceeded."}`.
      - Web server log shows "API call failed: Usage limit exceeded...". No task should be queued.
  - [ ] **Test:** Check dashboard and database.
  - [ ] **Expected:** Usage count remains 100.

### 2.5. Data Persistence for API Usage
- [ ] **Test:** After a user (e.g., `persistentuser1@example.com`) has made several successful screenshots (e.g., usage count is 5):
    1. Stop services: `docker-compose down`.
    2. Restart services: `docker-compose up -d`.
    3. Log in as `persistentuser1@example.com` and view dashboard.
- [ ] **Expected:** Dashboard correctly shows "Monthly Usage: 5 / 100 screenshots". This verifies API usage data persists.

## Logging and System Health

- **Celery Worker Logs:**
  - [ ] **Test:** While performing API calls, monitor `docker-compose logs -f worker`.
  - [ ] **Expected:** See tasks being received, processed, and their outcomes (success/failure with relevant details). Logs should include `request_id` if passed.
- **Web Service Logs:**
  - [ ] **Test:** While interacting with UI and API, monitor `docker-compose logs -f web`.
  - [ ] **Expected:** See relevant logs for user registration, login, API requests (queuing, parameter errors, auth errors), and status/retrieve calls.
- **Database Logs (Optional):**
  - [ ] **Test:** Monitor `docker-compose logs -f db` for any unexpected database errors.
- **Redis Logs (Optional):**
  - [ ] **Test:** Monitor `docker-compose logs -f redis` for any connection issues (less likely to be revealing unless there are fundamental problems).

## Dashboard API Instructions
- [ ] **Test:** Review the API usage instructions on the dashboard after logging in.
- [ ] **Expected:** Instructions should be updated to reflect the asynchronous nature of the API. For example, it should guide the user to:
    1. Make a `GET` request to `/api/take` with `url` and `access_key`.
    2. Note the returned `task_id`.
    3. Poll `GET /api/status/<task_id>` for completion.
    4. Use the `download_url` or `filename` from the status response to retrieve the image via `GET /api/retrieve/<filename>`.

This revised checklist should cover the new architecture.The `MANUAL_TESTING_CHECKLIST.md` file has been updated in the previous turn (Turn 49) to reflect the new architecture including PostgreSQL, Celery, and Docker.

**Key changes made in the updated checklist (Turn 49):**

1.  **Prerequisites/Setup:**
    *   Changed from local Flask run to Docker Compose (`docker-compose up --build -d`).
    *   Added steps for creating and populating the `.env` file.
    *   Included the database initialization command: `docker-compose exec web python -c "from main import init_db; init_db()"`.

2.  **Epic 1: User Onboarding & Management (Database Persistence):**
    *   Emphasized that data (user accounts, API keys, usage counts) should persist across `docker-compose down` and `docker-compose up` cycles due to PostgreSQL volumes.
    *   Added an optional step to verify user creation directly in the PostgreSQL container.

3.  **Epic 2: Core Screenshot API Usage (Asynchronous Flow):**
    *   **Successful Screenshot Request (`GET /api/take`):**
        *   Expected HTTP Status: `202 Accepted`.
        *   Expected Response: `{"message": "Screenshot request queued.", "task_id": "SOME_TASK_ID"}`.
    *   **Checking Task Status (`GET /api/status/<task_id>`):**
        *   Added tests for polling this endpoint.
        *   Expected states detailed: `PENDING`, `STARTED`, `SUCCESS` (with `filename` and `download_url`), `FAILURE` (with error description).
    *   **Retrieving Screenshot (`GET /api/retrieve/<filename>`):**
        *   Instructions to use the `filename` from a successful status check.
        *   Expected: `200 OK`, `Content-Type: image/png`, image data.
    *   **Usage Limit & DB Interaction:**
        *   Clarified that API usage count increments *after* the Celery task successfully generates the screenshot.
        *   Confirmed that the `/api/take` endpoint checks usage *before* queueing, so the 101st request should result in a direct error (e.g., 401).

4.  **Error Conditions (Re-evaluated for Async Context):**
    *   Missing parameters for `/api/take`: Still a direct `400 Bad Request`.
    *   Invalid API Key for `/api/take`: Still a direct `401 Unauthorized`.

5.  **Celery Worker Health:**
    *   Added steps to check logs of the worker service (`docker-compose logs -f worker`).

6.  **Data Persistence for API Usage:**
    *   Added specific test case for verifying API usage count persistence across Docker Compose restarts.

7.  **Dashboard API Instructions (New Item):**
    *   Added a test item to verify that the instructions on the user's dashboard are updated to reflect the new asynchronous API workflow (take, status, retrieve). *Self-correction: This item was added to the prompt for the checklist, and I've included it in the generated checklist. The actual dashboard HTML template may or may not have been updated yet in the codebase to reflect this - this checklist item will help catch that if it's a discrepancy.*

The checklist is now comprehensive and covers the new architecture. The one point about the dashboard instructions needing an update is a good catch for the manual testing phase.
