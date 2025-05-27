# Backend Overview

The backend is responsible for handling API requests, managing users, taking screenshots, and processing asynchronous tasks. It is built using a combination of Python-based technologies to ensure robustness and scalability.

## Core Components and Technologies

The backend relies on several key components and technologies:

### Flask

*   **Role:** Flask serves as the main web framework for the application. It is responsible for handling incoming HTTP requests, routing them to the appropriate handlers, rendering web pages for the frontend interface, and managing the API endpoints.
*   **Key Files/Modules:**
    *   `main.py`: This is the entry point of the Flask application, where the app is initialized and configured.
    *   `app/web/__init__.py`: Contains the routes and logic for the user-facing web pages (e.g., sign up, sign in, dashboard).
    *   `app/api/__init__.py`: Defines the routes and logic for the API, particularly the `/api/take` endpoint for screenshots.
*   **Configuration:** The Flask application uses a `SECRET_KEY` environment variable for session management and security.

### Celery

*   **Role:** Celery is used as an asynchronous task queue. Its primary function in this service is to offload the potentially time-consuming process of screenshot generation from the main web request-response cycle. This prevents API requests from timing out and improves the overall responsiveness of the service.
*   **Key Files/Modules:**
    *   `celery_worker.py`: This file likely defines the Celery application instance and the screenshot task(s) that workers will execute.
    *   `app/utils/screenshot_taker.py`: This utility module is expected to contain the core logic for capturing screenshots, which is then called by Celery tasks.

### PostgreSQL

*   **Role:** PostgreSQL is the primary relational database used for persistent storage. It stores crucial data such as user account information (usernames, hashed passwords), API keys, and potentially API usage data (e.g., number of screenshots taken by each user).
*   **Key Files/Modules:**
    *   `app/models/__init__.py`: This module typically contains the SQLAlchemy database models that define the schema for the tables (e.g., `User`, `APIKey`).
*   **Configuration:** The connection to the PostgreSQL database is configured via the `DATABASE_URL` environment variable.

### Redis

*   **Role:** Redis serves primarily as the message broker for Celery, facilitating communication between the Flask application (which produces tasks) and the Celery workers (which consume tasks). It can also be used for other purposes like caching, if implemented.
*   **Configuration:** The connection to the Redis server is configured via the `REDIS_URL` environment variable.

### Playwright

*   **Role:** Playwright is a browser automation library. It is the core tool used by the backend to interact with web pages and capture screenshots. It allows the service to control a browser instance (e.g., Chromium, Firefox, WebKit), navigate to a given URL, and save the rendered page as an image.
*   **Usage:**
    *   Playwright's installation is specified in `Dockerfile.web` and `Dockerfile.worker`, indicating it's a key dependency for both the web server (perhaps for initial validation or direct calls in some setups) and the Celery workers.
    *   The actual implementation of screenshot logic using Playwright is expected to be within `app/utils/screenshot_taker.py`.

## Screenshot Process

The process of generating a screenshot typically follows this flow:

1.  **API Request Received:** A user sends a `GET` request to the `/api/take` endpoint, including the `url` to capture and their `access_key`. This request is received by the Flask application.
2.  **Task Publication to Celery:** Flask validates the request and the API key. If valid, instead of generating the screenshot directly (which could be slow), Flask serializes the necessary information (e.g., the target URL) and publishes a new task to the Celery task queue (via Redis).
3.  **Celery Worker Task Execution:** A Celery worker process, running independently, picks up the task from the queue.
4.  **Screenshot Generation with Playwright:** The Celery worker executes the task, which involves calling the function in `app/utils/screenshot_taker.py`. This function uses Playwright to launch a browser, navigate to the specified URL, and capture the screenshot.
5.  **Screenshot Return:** Once the screenshot is generated (typically as a PNG image), it is returned in the HTTP response to the original API request. The `README.md` implies a direct return of the image data. The actual screenshot files might be temporarily stored, and their storage location can be configured with the `SCREENSHOT_OUTPUT_DIR` environment variable.

This asynchronous architecture ensures that the API can handle multiple requests efficiently and that users receive a timely response, even if the screenshot generation itself takes a few seconds.
