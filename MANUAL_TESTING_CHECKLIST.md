# Screenshot ONE - MVP: Manual Testing Checklist

## Prerequisites
- The application is running locally (e.g., `flask run` or `python main.py`).
- You have a web browser.
- You have a tool to make API requests (e.g., Postman, curl, or a browser's address bar for GET requests).

## Epic 1: User Onboarding & Management

### 1.1. Landing Page
- [ ] **Test:** Open the root URL (`/`).
- [ ] **Expected:** See "The Screenshot API for Developers" headline, description, and "Sign Up for Free" button.

### 1.2. User Signup
- [ ] **Test:** Click "Sign Up for Free" button or navigate to `/signup`.
- [ ] **Expected:** See signup form with Email and Password fields.
- [ ] **Test:** Enter a new email (e.g., `testuser1@example.com`) and a password. Click "Sign Up".
- [ ] **Expected:** Redirected to `/signin`. User data (hashed password, API key) should be in `users_db` (if inspecting server-side). Usage initialized to 0 in `usage_db`. Check server logs for "New user registered: testuser1@example.com" message.
- [ ] **Test:** Try signing up with an existing email (e.g., `testuser1@example.com` again).
- [ ] **Expected:** See an error message like "Email already exists". Redirected back to `/signup`.

### 1.3. User Signin
- [ ] **Test:** Navigate to `/signin`.
- [ ] **Expected:** See signin form.
- [ ] **Test:** Enter valid credentials for a registered user (e.g., `testuser1@example.com` and its password). Click "Sign In".
- [ ] **Expected:** Redirected to `/dashboard`. Check server logs for "User logged in: testuser1@example.com" message.
- [ ] **Test:** Enter invalid email or password.
- [ ] **Expected:** See an error message like "Invalid credentials". Redirected back to `/signin`.

### 1.4. Dashboard
- [ ] **Test:** After login, view the `/dashboard`.
- [ ] **Expected:**
    - Display the correct API key for the logged-in user.
    - Display "Monthly Usage: 0 / 100 screenshots" (for a new user or after usage reset).
    - Display API usage instructions: `GET /api/take?url=<URL_TO_CAPTURE>&access_key=<YOUR_API_KEY>`.
- [ ] **Test:** Access `/dashboard` without being logged in (e.g., in a new browser session or after clearing cookies).
- [ ] **Expected:** Redirected to `/signin`.

### 1.5. User Signout
- [ ] **Test:** On the dashboard, click the "Sign Out" link.
- [ ] **Expected:** Redirected to the landing page (`/`). Session should be cleared.
- [ ] **Test:** Try accessing `/dashboard` again after signout.
- [ ] **Expected:** Redirected to `/signin`.

## Epic 2: Core Screenshot API Usage (`GET /api/take`)

**Setup:**
- Ensure you have a valid `access_key` from the dashboard of a registered user.
- Choose a few test URLs (e.g., `https://example.com`, `https://playwright.dev`).

### 2.1. Successful Screenshot
- [ ] **Test:** Make a GET request: `/api/take?url=https://example.com&access_key=YOUR_VALID_ACCESS_KEY`
- [ ] **Expected:**
    - HTTP Status Code: 200 OK.
    - `Content-Type`: `image/png`.
    - Response body is a valid PNG image of the full page.
    - Server logs show "API call attempt..." and "Screenshot successful..." messages.
    - User's usage count in `usage_db` (and on dashboard after refresh) increments by 1.

### 2.2. Missing Parameters
- [ ] **Test:** Make a GET request: `/api/take?access_key=YOUR_VALID_ACCESS_KEY` (missing `url`)
- [ ] **Expected:**
    - HTTP Status Code: 400 Bad Request.
    - Response body: `{"error": "Missing or invalid parameters."}`
    - Server logs show "API call failed: Missing parameters..." warning.
- [ ] **Test:** Make a GET request: `/api/take?url=https://example.com` (missing `access_key`)
- [ ] **Expected:**
    - HTTP Status Code: 400 Bad Request.
    - Response body: `{"error": "Missing or invalid parameters."}`
    - Server logs show "API call failed: Missing parameters..." warning.

### 2.3. Invalid API Key
- [ ] **Test:** Make a GET request: `/api/take?url=https://example.com&access_key=INVALID_KEY_123`
- [ ] **Expected:**
    - HTTP Status Code: 401 Unauthorized.
    - Response body: `{"error": "Unauthorized or usage limit exceeded."}`
    - Server logs show "API call failed: Invalid access key INVALID_KEY_123..." warning.

### 2.4. Screenshot Timeout
- [ ] **Test:** Use a URL that is known to be very slow to load or non-existent (e.g., `http://thissitedoesnotexistandwilltimeout.com`). The default Playwright timeout is 30 seconds for navigation.
- [ ] **Expected (if timeout occurs):**
    - HTTP Status Code: 408 Request Timeout.
    - Response body: `{"error": "Screenshot generation timed out."}`
    - Server logs show "API call failed: Screenshot timeout for URL..." error.

### 2.5. Usage Limit Exceeded
- [ ] **Test:** For a specific user, make 100 successful API calls. (This might be time-consuming; alternatively, manually set a user's usage to 99 or 100 in `usage_db` if inspecting server-side for faster testing).
- [ ] **Expected:** Dashboard shows "100 / 100 screenshots" after 100 calls.
- [ ] **Test:** Make the 101st API call for that user.
- [ ] **Expected:**
    - HTTP Status Code: 401 Unauthorized.
    - Response body: `{"error": "Unauthorized or usage limit exceeded."}`
    - Server logs show "API call failed: Usage limit exceeded for user..." warning.
    - Usage count should remain 100.

### 2.6. Internal Server Error (Conceptual)
- [ ] **Test:** (Difficult to force reliably without code modification). This would typically be if Playwright's browser context cannot be created, or another unhandled server error occurs during the request. Review code for general `try...except Exception` blocks in the API route.
- [ ] **Expected (if such an error occurs):**
    - HTTP Status Code: 500 Internal Server Error.
    - Response body: `{"error": "Internal server error."}`
    - Server logs show the specific internal error, e.g., "API call failed: Internal server error during screenshot...".

## Logging
- [ ] **Test:** Perform various actions:
    - User signup (`testuser2@example.com`).
    - User signin (`testuser2@example.com`).
    - Successful API call (using `testuser2`'s API key).
    - API call with missing parameters.
    - API call with an invalid API key.
    - API call that times out.
    - API call for a user who has exceeded their usage limit.
- [ ] **Expected:** Check server logs (console output of `flask run` or `python main.py`). Relevant activities and errors should be logged with appropriate details (timestamps, log level, messages, user email/IP where relevant, URL for API calls). Each log should be on a new line.
```
