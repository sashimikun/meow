---
sidebar_label: 'Backend Architecture'
title: 'Backend Architecture'
---

# Backend Architecture

This section provides an overview of the components that make up the backend of the Screenshot API service.

The backend is designed with a microservices-like approach, separating the web application from resource-intensive screenshot processing. This is achieved by using a web server for handling immediate HTTP requests and a distributed task queue for asynchronous operations, ensuring the API remains responsive.

## Core Components

### Flask

*   **Role:** Flask is a lightweight WSGI web application framework in Python. It serves as the backbone for both the user-facing web interface and the core API.
    *   **Web Interface:** Handles requests for HTML pages, user authentication (signup, signin), and the user dashboard.
    *   **API Endpoint:** Manages the `/api/take` endpoint, validates incoming requests, and initiates screenshot tasks.
*   **Key Files/Directories:**
    *   `main.py`: The main entry point for the Flask application, containing app configuration and route definitions.
    *   `app/web/`: Contains blueprints and handlers for web-related routes (e.g., serving HTML templates).
    *   `app/api/`: Contains blueprints and handlers for API-specific routes, particularly `/api/take`.

### Celery

*   **Role:** Celery is an asynchronous task queue/job queue based on distributed message passing. It is used to offload the time-consuming process of taking screenshots from the main application thread. This prevents API requests from timing out and improves overall system responsiveness.
    *   When a screenshot request is received and validated by Flask, a task is sent to a Celery queue.
    *   Dedicated worker processes monitor this queue and execute the screenshot tasks asynchronously.
*   **Key Files/Directories:**
    *   `celery_worker.py`: Defines and configures the Celery application instance and its tasks. This is the entry point for Celery workers.
    *   `app/utils/screenshot_taker.py`: This utility, which uses Playwright to capture screenshots, is typically called by Celery tasks.

### Playwright

*   **Role:** Playwright is a Node.js library (with Python bindings) for browser automation. It is used to programmatically control a web browser to navigate to a URL, render the page, and capture a screenshot.
    *   The service is configured to use the Chromium browser engine via Playwright for consistent rendering. This is often specified in the Docker environment for the Celery workers (e.g., `Dockerfile.worker` would include Playwright installation and browser download commands).
*   **Key Files/Modules:**
    *   `app/utils/screenshot_taker.py`: Contains the logic for interacting with Playwright, including launching a browser, navigating to a page, and saving the screenshot.

### PostgreSQL

*   **Role:** PostgreSQL is a powerful, open-source object-relational database system. It serves as the primary persistent data store for the application.
    *   **User Data:** Stores user account information, including usernames (or emails) and hashed passwords.
    *   **API Keys:** Manages API keys associated with user accounts for authenticating API requests.
    *   **Usage Tracking:** Records API usage statistics, such as the number of screenshots taken by each user, to enforce monthly quotas.
*   **Key Files/Modules:**
    *   `app/models/__init__.py` (and any other files within `app/models/`): Defines the SQLAlchemy models that map to database tables (e.g., `User`, `APIKey`, `Usage`).

### Redis

*   **Role:** Redis is an in-memory data structure store, used as a distributed, in-memory key-value database, cache, and message broker.
    *   **Celery Message Broker:** Redis facilitates communication between the Flask application and Celery workers. When Flask publishes a task, it's placed on a queue in Redis. Celery workers listen to this queue for new tasks.
    *   **Celery Result Backend (Optional):** Redis can also be used by Celery to store the state and results of tasks, although this might not be explicitly used if the API simply returns the image directly upon task completion by the worker.

## Data Flow for a Screenshot Request

1.  **Request Reception:** A user sends a `GET` request to the `/api/take` endpoint with `url` and `access_key` parameters.
2.  **Flask Validation:** The Flask application receives the request.
    *   It authenticates the `access_key` by looking it up in the PostgreSQL database.
    *   It checks the user's current usage against their quota (also from PostgreSQL).
    *   It validates the `url` parameter.
3.  **Task Creation:** If validation is successful, Flask creates a new screenshot task and sends it to the Celery task queue (managed by Redis). The API might immediately return a pending status or hold the connection.
4.  **Worker Processing:** A Celery worker process, running independently, picks up the task from the Redis queue.
5.  **Screenshot Generation:** The Celery worker executes the task, which involves:
    *   Calling the `screenshot_taker.py` utility.
    *   `screenshot_taker.py` uses Playwright to launch a headless Chromium browser, navigate to the target URL, and capture the screenshot.
6.  **Result Handling:**
    *   The screenshot (as image data) is returned by Playwright.
    *   The Celery task can then store this image (e.g., temporarily in a file system or cloud storage) or directly return it.
    *   The Flask application, if it was holding the connection or if the client polls for results, receives the image data.
7.  **Response to User:** The Flask API sends the PNG image data back to the user as the HTTP response body with a `Content-Type: image/png` header. If an error occurred during the process, an appropriate JSON error response is sent.

This architecture allows the service to handle multiple screenshot requests efficiently and reliably.
