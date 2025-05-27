---
sidebar_label: 'Development Setup'
title: 'Development Setup Guide'
---

# Development Setup Guide

This guide explains how to set up the project for local development and testing, enabling you to contribute to the Screenshot API Service.

## Local Development Options

Developers have two primary options for setting up a local development environment:

1.  **Python Virtual Environment:** A traditional setup using Python's `venv` module, giving you direct control over dependencies and environment variables.
2.  **Docker Compose:** Utilizes Docker to run the application and its services (PostgreSQL, Redis) in isolated containers. This method ensures consistency with the production environment and simplifies service management.

Choose the method that best suits your workflow and tooling preferences.

## Python Virtual Environment Setup

This setup involves configuring your local machine with the necessary services and Python environment.

### Steps:

1.  **Prerequisites:**
    *   Ensure you have Python 3.8+ and `pip` (Python package installer) installed.
    *   A running PostgreSQL server instance.
    *   A running Redis server instance (e.g., `sudo apt install redis-server` or run via Docker).

2.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```
    (Replace `<your-repository-url>` and `<repository-name>` accordingly.)

3.  **Set Up Virtual Environment:**
    Create and activate a Python virtual environment to isolate project dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Configure Environment Variables:**
    Set the following environment variables for your local development session. These are typically set in your shell's configuration file (e.g., `.bashrc`, `.zshrc`) or exported directly in your terminal:
    *   `SECRET_KEY`: A secret key for Flask session management. For development, this can be a simple string, but ensure it's strong for any production-like testing.
        ```bash
        export SECRET_KEY='your_development_secret_key'
        ```
    *   `DATABASE_URL`: The connection string for your local PostgreSQL database.
        ```bash
        export DATABASE_URL='postgresql://your_local_db_user:your_local_db_password@localhost:5432/your_local_db_name'
        ```
        (Adjust user, password, and database name as per your PostgreSQL setup.)
    *   `REDIS_URL`: The connection string for your local Redis server.
        ```bash
        export REDIS_URL='redis://localhost:6379/0'
        ```
    *   `SCREENSHOT_OUTPUT_DIR`: (Optional) Path to store screenshots. Defaults to `/tmp/screenshots` if not set.
        ```bash
        export SCREENSHOT_OUTPUT_DIR='/path/to/your/local/screenshots_directory'
        ```

5.  **Install Dependencies:**
    Install the required Python packages and Playwright browser binaries:
    ```bash
    pip install -r requirements.txt
    playwright install --with-deps chromium # Installs Chromium and its OS dependencies
    ```

6.  **Initialize the Database:**
    The first time you run the application, or if you've made changes to database models, create the database tables:
    ```bash
    export FLASK_APP=main.py
    flask shell
    >>> from main import init_db
    >>> init_db()
    >>> exit()
    ```
    Alternatively, you can temporarily uncomment the `init_db()` call in `main.py` and run `python main.py` once.

7.  **Run the Application (Flask):**
    Start the Flask development server:
    ```bash
    export FLASK_APP=main.py # Ensure FLASK_APP is set
    flask run
    ```
    Or, for development with auto-reload (if `init_db()` is commented out in `main.py`):
    ```bash
    python main.py
    ```
    The application will typically be available at `http://127.0.0.1:5000`.

8.  **Run the Celery Worker:**
    Open a new terminal, activate the virtual environment, and start the Celery worker for background screenshot processing:
    ```bash
    celery -A celery_worker.celery_app worker -l info
    ```

## Docker-based Development Setup

This method uses Docker Compose to manage the application and its services, as detailed in the "Running with Docker Compose" section of the `README.md` and the [Deployment Guide](./deployment.md#docker-based-deployment-recommended). It is highly recommended for a consistent development experience.

### Key Steps:

1.  **Prerequisites:**
    *   Install Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    *   Install Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

2.  **Create `.env` File:**
    Create a `.env` file in the project root as described in the [Deployment Guide](./deployment.md#environment-configuration-env-file). For development, you can use less complex passwords if preferred, but ensure `SECRET_KEY` is set.

3.  **Build and Run Services:**
    Open a terminal in the project root and run:
    ```bash
    docker-compose up --build
    ```
    *   `--build`: Rebuilds images if Dockerfiles or code have changed.
    *   Omitting `-d` (detached mode) is useful for development as it keeps logs from all services (web, worker, db, redis) in the foreground of your terminal. Press `Ctrl+C` to stop.

4.  **Initialize Database (First Time Only):**
    If this is your first time running with Docker or if the database volume was removed, initialize the database schema. In a new terminal:
    ```bash
    docker-compose exec web python -c "from main import init_db; init_db()"
    ```

5.  **Code Mounting and Auto-Reload:**
    The `docker-compose.yml` is configured to mount the current project directory (`./`) into the `/app` directory inside the `web` and `worker` containers.
    *   Flask's development server (used by default with `flask run` or `python main.py` in the `Dockerfile.web` if Gunicorn is not explicitly forced for dev) will automatically reload on Python code changes.
    *   For the Celery worker, you might need to restart the `docker-compose` session (Ctrl+C and `docker-compose up --build`) if you make changes to task definitions or other modules it imports at startup.

## Running Tests

The project uses Python's built-in `unittest` framework. Tests are located in the `tests/` directory and include:
*   `test_api.py`: For API endpoint tests.
*   `test_models.py`: For database model tests.
*   `test_web.py`: For web interface (routes, views) tests.

To run all tests, navigate to the project root directory in your terminal and execute:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Ensure your development environment (either virtualenv or Docker services) is properly configured and running, especially if tests interact with the database or other services. For Docker, you might run tests within the `web` container:

```bash
docker-compose exec web python -m unittest discover -s tests -p "test_*.py"
```

## Contribution Guidelines

Currently, formal contribution guidelines (e.g., `CONTRIBUTING.md`) are not established. However, if you plan to contribute, please consider the following:

*   **Code Style:** Follow PEP 8 guidelines for Python code.
*   **Branching:** Create feature branches for new development (e.g., `feature/your-feature-name`).
*   **Commits:** Write clear and concise commit messages.
*   **Tests:** Add tests for new features or bug fixes. Ensure all tests pass before submitting changes.

As the project matures, more detailed contribution guidelines may be provided.
