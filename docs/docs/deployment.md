---
sidebar_label: 'Deployment'
title: 'Deployment Guide'
---

# Deployment Guide

This guide provides instructions for deploying the Screenshot API Service.

## Overview

The primary and recommended method for deploying the Screenshot API Service is using Docker and Docker Compose. This approach simplifies dependency management and provides a consistent environment. A manual deployment approach is also outlined for scenarios where Docker is not suitable.

## Docker-based Deployment (Recommended)

Using Docker Compose is the recommended way to get the service and its dependencies (PostgreSQL, Redis) up and running quickly. The configuration is defined in the `docker-compose.yml` file at the root of the project.

### Steps:

1.  **Prerequisites:**
    *   Ensure you have Docker installed: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    *   Ensure you have Docker Compose installed: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/) (often included with Docker Desktop).

2.  **Environment Configuration (`.env` file):**
    Create a `.env` file in the project root directory. Docker Compose will automatically use this file to set environment variables for the services.
    ```env
    # .env - Sample configuration
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=screenshotone_db

    # Ensure this matches the PostgreSQL credentials above
    DATABASE_URL=postgresql://user:password@db/screenshotone_db

    REDIS_URL=redis://redis:6379/0

    # IMPORTANT: Replace with a strong, unique key for production!
    SECRET_KEY=your_production_secret_key_here

    # Optional: Output directory for screenshots within Docker.
    # Defaults to /app/screenshots_output as set in docker-compose.yml
    # SCREENSHOT_OUTPUT_DIR=/app/custom_screenshots_output
    ```
    **Note:** For production, it is critical to set a strong, unique `SECRET_KEY`.

3.  **Build and Run Services:**
    Open a terminal in the project root and run:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Forces Docker Compose to rebuild the images if they don't exist or if the Dockerfiles or application code have changed.
    *   `-d`: Runs the services in detached mode (in the background).

4.  **Database Initialization (First Time Only):**
    After the services have started (especially the `db` service), you need to initialize the database schema. Open another terminal and run:
    ```bash
    docker-compose exec web python -c "from main import init_db; init_db()"
    ```
    You should see a message like "Database tables created (if they didn't exist)."

5.  **Accessing the Application:**
    Once running, the web application should be accessible at:
    *   `http://localhost:8000`
    The API endpoints will be available under this base URL (e.g., `http://localhost:8000/api/take`).

6.  **Viewing Logs:**
    To view the logs from all running services:
    ```bash
    docker-compose logs -f
    ```
    To view logs for specific services (e.g., `web` or `worker`):
    ```bash
    docker-compose logs -f web
    docker-compose logs -f worker
    ```

7.  **Stopping the Application:**
    To stop all services:
    ```bash
    docker-compose down
    ```
    To stop services and remove associated volumes (including database data and screenshots stored in Docker volumes):
    ```bash
    docker-compose down -v
    ```

## Manual/Conceptual Deployment (Alternative)

For environments where Docker is not an option, the following steps outline a conceptual approach based on the information in `README.md`.

1.  **Choosing a Platform:**
    *   **Virtual Machines (VMs):** Offers full control (e.g., AWS EC2, Google Compute Engine, Azure VMs).
    *   **Platform as a Service (PaaS):** Simplifies deployment and scaling (e.g., Google Cloud Run, AWS Elastic Beanstalk/App Runner, Heroku). PaaS platforms may handle some of the steps below automatically.

2.  **Environment Setup:**
    *   Install Python (3.8+).
    *   Clone the repository.
    *   Set up a Python virtual environment.
    *   Install dependencies: `pip install -r requirements.txt`.
    *   Install Playwright and its browser binaries: `playwright install --with-deps chromium`.
    *   Set up and run a PostgreSQL server instance.
    *   Set up and run a Redis server instance.

3.  **Application Configuration (Environment Variables):**
    Configure the necessary environment variables (see the "Environment Variables" section below for details). These are crucial for the application to connect to services and run correctly.

4.  **Running the Application Components:**
    *   **Flask Web Application:** Use a production-grade WSGI server like Gunicorn.
        ```bash
        gunicorn --workers 4 --bind 0.0.0.0:8000 'main:app' --timeout 120
        ```
        (Adjust host, port, and worker count as needed.)
    *   **Celery Worker:** Start the Celery worker process.
        ```bash
        celery -A celery_worker.celery_app worker -l info --concurrency=2
        ```
        (Adjust concurrency as needed.)

5.  **HTTPS Configuration:**
    *   **Crucial for security.** Do not run in production without HTTPS.
    *   Set up a reverse proxy (e.g., Nginx, Caddy) in front of the Gunicorn WSGI server. The reverse proxy will handle SSL/TLS termination and forward requests to the application.
    *   PaaS platforms often provide built-in SSL/TLS termination.

6.  **Process Management:**
    *   **On a VM:** Use a process manager like `systemd` or `supervisor` to ensure the Gunicorn (Flask app) and Celery worker processes are managed, restarted on failure, and started on boot.
    *   **On PaaS:** Process management is typically handled by the platform.

## Environment Variables

The following environment variables are critical for configuring the application:

*   `SECRET_KEY`: A strong, unique secret key used by Flask for session management and cryptographic signing. **Must be changed for production.**
*   `DATABASE_URL`: The connection string for the PostgreSQL database.
    *   Format: `postgresql://your_db_user:your_db_password@your_db_host:your_db_port/your_db_name`
*   `REDIS_URL`: The connection string for the Redis server, used by Celery as a message broker.
    *   Format: `redis://your_redis_host:your_redis_port/0`
*   `SCREENSHOT_OUTPUT_DIR`: (Optional) The directory where generated screenshots are stored.
    *   In Docker, this defaults to `/app/screenshots_output` (a shared volume). For manual deployments, ensure this path exists and is writable.
*   `FLASK_APP` (e.g., `main:app`): Tells Flask how to import the application. This is typically set to `main:app` for this project and is often configured in the `Dockerfile.web` or process manager.

## Security Considerations (Production)

When deploying to a production environment, ensure you address the following security points:

*   **Strong `SECRET_KEY`**: Always use a unique, long, and random string for the `SECRET_KEY` environment variable. Do not use the default or example keys.
*   **HTTPS**: Serve the application exclusively over HTTPS. Use a reverse proxy like Nginx or Caddy to handle SSL/TLS termination.
*   **Input Validation**: While the application has basic validation, consider further hardening of input validation for the API endpoint (e.g., URL formats, length limits) to prevent potential abuse.
*   **Generic Error Messages**: For user-facing errors, provide generic messages. Log detailed error information internally for debugging, but avoid exposing stack traces or internal details to the public.
*   **Keep Dependencies Updated**: Regularly update all dependencies (Python packages, OS packages, Docker images) to patch known vulnerabilities.
*   **Resource Limits**: The screenshot process using Playwright can be resource-intensive. For production, implement robust resource limiting (CPU, memory) for the browser instances and Celery workers to prevent denial-of-service or performance degradation.
*   **Database Security**: Secure your PostgreSQL database with strong credentials, network restrictions (if applicable), and regular backups.
*   **Redis Security**: Secure your Redis instance, especially if exposed beyond the local deployment environment.

By following these guidelines, you can deploy the Screenshot API Service more securely and reliably.
