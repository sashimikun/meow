# Deployment

This section describes how to deploy the Screenshot API service. The recommended method for most environments is using Docker Compose.

## Docker Compose Deployment (Recommended)

This is the primary method detailed in the project's `README.md` for running the service, especially for development and testing, but also as a solid foundation for production deployments. It orchestrates all the necessary services (web application, database, message broker, and workers) in a containerized environment.

### Summary of Steps:

1.  **Prerequisites:**
    *   Ensure you have Docker installed: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    *   Ensure you have Docker Compose installed: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/) (often included with Docker Desktop).

2.  **Environment Configuration (`.env` file):**
    *   Create a `.env` file in the project root directory. This file will be automatically used by Docker Compose to set environment variables for the services.
    *   Example content for `.env`:
        ```env
        POSTGRES_USER=user
        POSTGRES_PASSWORD=password
        POSTGRES_DB=screenshotone_db
        DATABASE_URL=postgresql://user:password@db/screenshotone_db
        REDIS_URL=redis://redis:6379/0
        SECRET_KEY=your_strong_random_secret_key
        # SCREENSHOT_OUTPUT_DIR=/app/screenshots_output # Default in docker-compose
        ```
    *   **Important:** Replace `your_strong_random_secret_key` with a real, strong secret key, especially for production.

3.  **Build and Run Services:**
    *   Open a terminal in the project root and run:
        ```bash
        docker-compose up --build -d
        ```
    *   `--build`: Forces Docker Compose to rebuild the images if they don't exist or if the Dockerfiles/code have changed.
    *   `-d`: Runs the services in detached mode (in the background).

4.  **Initialize the Database (First Time Only):**
    *   After the services have started (especially the `db` service), you need to initialize the database schema. Open another terminal and run:
        ```bash
        docker-compose exec web python -c "from main import init_db; init_db()"
        ```

5.  **Accessing the Application:**
    *   The web application should be accessible at `http://localhost:8000`.
    *   The API endpoints will also be available under this base URL (e.g., `http://localhost:8000/api/take`).

6.  **Stopping the Application:**
    *   To stop all services:
        ```bash
        docker-compose down
        ```
    *   To stop and remove volumes (database data, screenshot data):
        ```bash
        docker-compose down -v
        ```

### Key Configuration Files:

*   `docker-compose.yml`: Defines the services (web, worker, db, redis), their configurations, networks, and volumes.
*   `Dockerfile.web`: Defines the Docker image for the Flask web application, including installing dependencies, Playwright, and Gunicorn.
*   `Dockerfile.worker`: Defines the Docker image for the Celery worker, including installing dependencies and Playwright.

## Environment Variables

These environment variables are crucial for configuring the application, whether running via Docker Compose or a manual setup.

*   `POSTGRES_USER`: Username for the PostgreSQL database. (Used by `db` service in Docker Compose, and to construct `DATABASE_URL`)
*   `POSTGRES_PASSWORD`: Password for the PostgreSQL database. (Used by `db` service in Docker Compose, and to construct `DATABASE_URL`)
*   `POSTGRES_DB`: Name of the PostgreSQL database. (Used by `db` service in Docker Compose, and to construct `DATABASE_URL`)
*   `DATABASE_URL`: The full connection string for the PostgreSQL database (e.g., `postgresql://user:password@host:port/dbname`). Used by the Flask app and Celery workers.
*   `REDIS_URL`: The connection string for the Redis server, used as a Celery broker (e.g., `redis://host:port/0`). Used by the Flask app and Celery workers.
*   `SECRET_KEY`: A strong, unique secret key used by Flask for session management and cryptographic signing. **Critical for security.**
*   `FLASK_APP`: Specifies the entry point for the Flask application (e.g., `main:app`). Often set within the `Dockerfile.web` but can be overridden.
*   `SCREENSHOT_OUTPUT_DIR`: The directory where captured screenshots are stored. Defaults to `/tmp/screenshots` if not set, or `/app/screenshots_output` within the Docker containers as per `docker-compose.yml`.
*   `PYTHONUNBUFFERED`: Set to `1` to ensure Python output (e.g., logs) is sent directly to the terminal without buffering, which is good practice for containerized applications. Set in `Dockerfile.web` and `Dockerfile.worker`.

## Manual/Conceptual Deployment (Advanced)

For environments where Docker Compose is not suitable (e.g., specific VM setups or certain PaaS), a manual deployment approach can be followed. The `README.md` outlines these conceptual steps:

1.  **Choosing a Platform:** This could be Virtual Machines (VMs) on cloud providers (AWS EC2, Google Compute Engine, Azure VMs) or Platform as a Service (PaaS) offerings (Google Cloud Run, AWS Elastic Beanstalk, Heroku).
2.  **Environment Setup:**
    *   Install Python, pip, and any system-level dependencies (including those for Playwright).
    *   Clone the application repository.
    *   Install Python dependencies from `requirements.txt`.
    *   Install Playwright browser binaries (`playwright install`).
    *   Set up PostgreSQL and Redis instances (either self-hosted or managed services).
3.  **Application Configuration:** Set all the necessary environment variables listed in the section above.
4.  **Running Application Components:**
    *   **Web Server:** Use a production-grade WSGI server like Gunicorn (as used in `Dockerfile.web`) or uWSGI to run the Flask application. Example: `gunicorn --workers 4 --bind 0.0.0.0:8000 'main:app'`.
    *   **Celery Workers:** Start Celery worker processes: `celery -A celery_worker.celery_app worker -l info`.
5.  **HTTPS Configuration:**
    *   **Crucial:** Serve the application over HTTPS in production.
    *   This is typically handled by a reverse proxy (e.g., Nginx, Caddy) placed in front of the WSGI server. The reverse proxy manages SSL/TLS termination. PaaS platforms often provide built-in SSL/TLS.
6.  **Process Management:**
    *   On VMs, use a process manager like `systemd` or `supervisor` to ensure the WSGI server and Celery workers are managed (e.g., started on boot, restarted on failure).
    *   PaaS solutions usually have their own mechanisms for managing application processes and background workers.

## Security Considerations (Production)

When deploying to a production environment, the following security aspects (highlighted in `README.md`) are critical:

*   **Strong `SECRET_KEY`**: Ensure the `SECRET_KEY` environment variable is set to a long, random, and unique string. Do not use default or easily guessable keys.
*   **HTTPS Everywhere**: Always serve the application over HTTPS. This encrypts data in transit between users and the server. Configure your reverse proxy or PaaS to handle SSL/TLS termination.
*   **Input Validation**: While basic validation is in place, consider further hardening of input validation for API endpoints, especially for the `url` parameter to prevent potential abuse.
*   **Generic Error Messages**: For user-facing errors, provide generic messages. Log detailed error information internally for debugging, but avoid exposing stack traces or internal details to the public.
*   **Keep Dependencies Updated**: Regularly update all dependencies (Python packages, system libraries, Docker base images) to patch known vulnerabilities.
*   **Resource Limits**: The screenshot generation process can be resource-intensive. For production, consider implementing robust resource limiting (CPU, memory) for the browser instances spawned by Playwright to prevent denial-of-service or performance degradation due to abuse or runaway processes. This might involve container resource limits or more fine-grained controls within the application.
