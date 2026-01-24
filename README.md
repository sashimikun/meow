# Screenshot API Services

This service provides an API to capture screenshots of web pages. Users can sign up, get an API key, and use it to request screenshots.

## Features

*   User registration and login
*   API key generation
*   Screenshot API endpoint (`/api/take`)
*   Usage tracking (100 screenshots per user per month)

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── screenshot_taker.py
│   └── web/
│       ├── __init__.py
│       ├── static/
│       │   └── .gitkeep
│       └── templates/
│           ├── dashboard.html
│           ├── index.html
│           ├── signin.html
│           └── signup.html
├── main.py
├── requirements.txt
├── README.md
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_models.py
    └── test_web.py
```

## Setup and Running

1.  **Prerequisites:**
    *   Ensure you have Python 3.8+ and pip installed.
    *   A running PostgreSQL server instance.
    *   A running Redis server instance (e.g., `sudo apt install redis-server` or run via Docker).

2.  **Clone the repository.**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

3.  **Set up a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Configure Environment Variables:**
    *   **`SECRET_KEY`**: Set a strong secret key for Flask session management.
        ```bash
        export SECRET_KEY='your_strong_random_secret_key_here'
        ```
    *   **`DATABASE_URL`**: Set the PostgreSQL connection string.
        ```bash
        export DATABASE_URL='postgresql://your_db_user:your_db_password@your_db_host:your_db_port/your_db_name'
        ```
        Example: `export DATABASE_URL='postgresql://user:password@localhost:5432/screenshotone_db'`
    *   **`REDIS_URL`**: Set the Redis connection string for Celery.
        ```bash
        export REDIS_URL='redis://localhost:6379/0'
        ```
    *   **`SCREENSHOT_OUTPUT_DIR`**: (Optional) Path to store screenshots. Defaults to `/tmp/screenshots`.
        ```bash
        export SCREENSHOT_OUTPUT_DIR='/path/to/your/screenshots_directory'
        ```

5.  **Install dependencies:**
    The application now uses PostgreSQL, Redis, Celery, Flask-SQLAlchemy, etc.
    ```bash
    pip install -r requirements.txt
    playwright install # To install necessary browser binaries
    ```

6.  **Initialize the Database:**
    The first time you run the application, or if you've made changes to the database models, you'll need to create the database tables.
    You can do this by temporarily uncommenting the `init_db()` call in the `if __name__ == '__main__':` block at the end of `main.py` and running `python main.py` once.
    Alternatively, you can use the Flask shell:
    ```bash
    export FLASK_APP=main.py
    flask shell
    >>> from main import init_db
    >>> init_db()
    >>> exit()
    ```
    **Note:** For production, database migrations (e.g., using Alembic) are recommended for managing schema changes.

7.  **Run the application:**
    ```bash
    export FLASK_APP=main.py # Ensure FLASK_APP is set if not already
    flask run
    ```
    Or for development with auto-reload (if you commented out `init_db()` again):
    ```bash
    python main.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

7.  **Run the Celery Worker:**
    Open a new terminal, activate the virtual environment, and start the Celery worker:
    ```bash
    celery -A celery_worker.celery_app worker -l info
    ```
    (Ensure `celery_worker.py` is in your `PYTHONPATH` or run from the project root where it can be found.)

## Getting Started with the API

This guide explains how to use the Screenshot API to capture web pages.

### Prerequisites

1.  **Obtain an Access Key:** You need an `access_key` to use the API.
    *   Sign up for an account on the web portal (available at the root URL, e.g., `http://localhost:5000/`).
    *   After signing in, your unique `access_key` will be displayed on your dashboard.

### API Endpoint

The API endpoint for taking screenshots is:

*   `GET /api/take`

### Request Parameters

The following query parameters are required for each request:

*   `url` (String, Required): The full URL of the web page you want to capture (e.g., `https://example.com`).
*   `access_key` (String, Required): Your unique API access key obtained from your dashboard.

### Example Request

You can use `curl` or any HTTP client to make requests. Here's an example using `curl`:

```bash
curl "http://localhost:5000/api/take?url=https://example.com&access_key=YOUR_ACCESS_KEY" -o screenshot.png
```

**Note:**
*   Replace `http://localhost:5000` with the actual base URL of the deployed API service if it's different.
*   Replace `YOUR_ACCESS_KEY` with the actual access key from your dashboard.
*   The `-o screenshot.png` flag will save the output image to a file named `screenshot.png`.

### Responses

#### Success Response

*   **`200 OK`**:
    *   `Content-Type: image/png`
    *   The body of the response is the PNG image data of the captured web page.

#### Common Error Responses

*   **`400 Bad Request`**: Indicates that one or more required parameters (`url` or `access_key`) are missing or incorrectly formatted.
    ```json
    {"error": "Missing or invalid parameters."}
    ```
*   **`401 Unauthorized`**: Indicates that the provided `access_key` is invalid, or your account has exceeded the monthly usage limit (100 screenshots).
    ```json
    {"error": "Unauthorized or usage limit exceeded."}
    ```
*   **`408 Request Timeout`**: Indicates that the screenshot generation process for the requested URL took longer than the server's allowed time (currently 30 seconds for page navigation).
    ```json
    {"error": "Screenshot generation timed out."}
    ```
*   **`500 Internal Server Error`**: Indicates an unexpected issue occurred on the server while trying to process the request.
    ```json
    {"error": "Internal server error."}
    ```

## Deployment

For production deployments, it is crucial to configure a reverse proxy (e.g., Nginx, Caddy) or use a platform service (e.g., AWS API Gateway, Google Cloud Load Balancing) to handle SSL/TLS termination and serve the application over HTTPS. The application itself runs on HTTP and relies on the deployment environment for HTTPS.

## Security Considerations

*   **Secret Key**: Ensure `app.secret_key` in `main.py` is replaced with a strong, randomly generated secret key for production environments.
*   **HTTPS**: As mentioned in the Deployment section, always serve this application over HTTPS in production.
*   **Input Validation**: While basic validation is in place, further hardening of input validation for the API endpoint (e.g., URL format) is recommended.
*   **Error Handling**: Current error messages might expose internal details. For production, consider more generic error messages for users while logging detailed errors internally.
*   **Dependencies**: Keep dependencies updated to avoid known vulnerabilities.
*   **Resource Limits**: The current screenshot utility and API have basic timeouts. For production, consider more robust resource limiting (CPU, memory) for the browser instances spawned by Playwright to prevent abuse.

## Conceptual Deployment Steps

This section outlines a high-level approach to deploying the Screenshot ONE MVP.

1.  **Choosing a Platform:**
    *   **Virtual Machines (VMs):** Offers full control (e.g., AWS EC2, Google Compute Engine, Azure VMs).
    *   **Platform as a Service (PaaS):** Simplifies deployment and scaling (e.g., Google Cloud Run, AWS Elastic Beanstalk/App Runner, Heroku).

2.  **Environment Setup (Illustrative for a VM):**
    *   Install Python (e.g., via `apt-get`, `yum`, or from source).
    *   Clone the repository: `git clone <repository_url>`
    *   Install Python dependencies: `pip install -r requirements.txt`
    *   Install Playwright browsers: `playwright install`
    *   Install Playwright system dependencies (as detailed in local setup).
    *   Install Redis server or configure connection to a managed Redis service.

3.  **Application Configuration (Environment Variables):**
    *   `FLASK_APP=main.py`
    *   `SECRET_KEY` (strong, unique value)
    *   `DATABASE_URL` (connection string for PostgreSQL)
    *   `REDIS_URL` (connection string for Celery broker/backend)
    *   `SCREENSHOT_OUTPUT_DIR` (path for storing screenshots)

4.  **Running the Application Components (Production):**
    *   Use a production-grade WSGI server like Gunicorn or uWSGI instead of Flask's built-in development server.
    *   Example Gunicorn command: `gunicorn --workers 4 --bind 0.0.0.0:8000 'main:app'` (The application will listen on port 8000 on all network interfaces).

5.  **HTTPS Configuration:**
    *   **Crucial for security.** Do not run in production without HTTPS.
    *   Typically handled by a reverse proxy (e.g., Nginx, Caddy) placed in front of the WSGI server. The reverse proxy handles SSL/TLS termination.
    *   PaaS platforms often provide built-in SSL/TLS termination through their load balancers or custom domain configurations.

6.  **Process Management:**
    *   **On a VM:**
        *   Use a process manager like `systemd` or `supervisor` to manage:
            *   The Gunicorn (or uWSGI) process for the Flask app.
            *   The Celery worker process(es).
    *   **On PaaS:**
        *   The Flask app is usually run as specified by the PaaS (e.g., via a Procfile for Heroku, or container entrypoint for Cloud Run).
        *   Celery workers need to be run as separate processes/services. Many PaaS provide ways to run background workers (e.g., Heroku worker dynos, AWS ECS services for background tasks).

## Running with Docker Compose

This is the recommended way to run the application for local development and testing.

1.  **Prerequisites:**
    *   Install Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    *   Install Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/) (often included with Docker Desktop).

2.  **Environment Configuration (`.env` file):**
    Create a `.env` file in the project root directory. This file will be automatically used by Docker Compose to set environment variables.
    ```env
    # .env
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=screenshotone_db

    # Make sure this matches the DATABASE_URL in docker-compose.yml for web/worker services
    # (specifically the user, password, and db name parts)
    DATABASE_URL=postgresql://user:password@db/screenshotone_db

    REDIS_URL=redis://redis:6379/0

    SECRET_KEY=your_super_secret_and_random_flask_key_here_for_docker

    # Optional: If you want to specify a different output directory for screenshots
    # SCREENSHOT_OUTPUT_DIR=/app/screenshots_output # This is the default in docker-compose.yml
    ```
    **Important:** Replace `your_super_secret_and_random_flask_key_here_for_docker` with a real, strong secret key.

3.  **Build and Run Services:**
    Open a terminal in the project root and run:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Forces Docker Compose to rebuild the images if they don't exist or if the Dockerfiles/code have changed.
    *   `-d`: Runs the services in detached mode (in the background).

4.  **Initialize the Database (First Time Only):**
    After the services have started (especially the `db` service), you need to initialize the database schema. Open another terminal and run:
    ```bash
    docker-compose exec web python -c "from main import init_db; init_db()"
    ```
    You should see a message like "Database tables created (if they didn't exist)."

5.  **Accessing the Application:**
    *   Web application: `http://localhost:8000`
    *   API: `http://localhost:8000/api/...`

6.  **Viewing Logs:**
    To view the logs from all services:
    ```bash
    docker-compose logs -f
    ```
    To view logs for specific services:
    ```bash
    docker-compose logs -f web
    docker-compose logs -f worker
    docker-compose logs -f db
    docker-compose logs -f redis
    ```

7.  **Stopping the Application:**
    To stop all services:
    ```bash
    docker-compose down
    ```
    If you want to also remove the named volumes (database data, screenshot data):
    ```bash
    docker-compose down -v
    ```
