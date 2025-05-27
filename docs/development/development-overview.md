# Development Environment Setup

This section explains how to set up a local development environment for working on the Screenshot API service. You can choose between a local Python environment or a Docker-based setup.

## Option 1: Local Python Virtual Environment

This approach involves setting up all services (Python, PostgreSQL, Redis) directly on your development machine.

1.  **Prerequisites:**
    *   Ensure you have Python 3.8+ and pip installed.
    *   A running PostgreSQL server instance.
    *   A running Redis server instance (e.g., `sudo apt install redis-server` or run via Docker).

2.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```
    (Replace `<your-repository-url>` and `<repository-name>` with the actual values.)

3.  **Set up a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Configure Environment Variables:**
    Set the following environment variables in your shell:
    *   `SECRET_KEY`: A strong secret key for Flask session management.
        ```bash
        export SECRET_KEY='your_strong_random_secret_key_here'
        ```
    *   `DATABASE_URL`: The PostgreSQL connection string.
        ```bash
        export DATABASE_URL='postgresql://your_db_user:your_db_password@your_db_host:your_db_port/your_db_name'
        ```
        (Example: `export DATABASE_URL='postgresql://user:password@localhost:5432/screenshotone_db'`)
    *   `REDIS_URL`: The Redis connection string for Celery.
        ```bash
        export REDIS_URL='redis://localhost:6379/0'
        ```
    *   `SCREENSHOT_OUTPUT_DIR`: (Optional) Path to store screenshots. Defaults to `/tmp/screenshots`.
        ```bash
        export SCREENSHOT_OUTPUT_DIR='/path/to/your/screenshots_directory'
        ```

5.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install # To install necessary browser binaries
    ```

6.  **Initialize the Database:**
    The first time you run the application, or if you've made changes to the database models, create the database tables.
    Using the Flask shell:
    ```bash
    export FLASK_APP=main.py
    flask shell
    >>> from main import init_db
    >>> init_db()
    >>> exit()
    ```
    Alternatively, you can temporarily uncomment the `init_db()` call in `main.py` and run `python main.py` once.

7.  **Run the Flask application:**
    ```bash
    export FLASK_APP=main.py # Ensure FLASK_APP is set
    flask run
    ```
    Or for development with auto-reload (if you've re-commented `init_db()` in `main.py`):
    ```bash
    python main.py
    ```
    The application will typically be available at `http://127.0.0.1:5000`.

8.  **Run the Celery Worker:**
    Open a new terminal, activate the virtual environment, and start the Celery worker:
    ```bash
    celery -A celery_worker.celery_app worker -l info
    ```

## Option 2: Docker Compose Environment (Recommended for Development)

Using Docker Compose is often simpler for development as it manages all the services (web app, database, Redis, worker) in isolated containers.

*   **Setup:**
    1.  Create a `.env` file in the project root by copying the example from the `README.md` or the "Docker Compose Deployment" section in the **Deployment** documentation. Ensure `SECRET_KEY`, `DATABASE_URL`, and `REDIS_URL` are correctly configured for the Docker environment (e.g., `DATABASE_URL=postgresql://user:password@db/screenshotone_db`, `REDIS_URL=redis://redis:6379/0`).
    2.  Build and start all services:
        ```bash
        docker-compose up --build -d
        ```
    3.  Initialize the database (first time only, after services are running):
        ```bash
        docker-compose exec web python -c "from main import init_db; init_db()"
        ```
*   **Development Workflow:** The project code is typically mounted as a volume into the `web` and `worker` containers (as defined in `docker-compose.yml`). This means changes you make to your local code will be reflected automatically inside the containers, often triggering an auto-reload of the Flask development server.

For more details on Docker Compose usage (accessing logs, stopping services, etc.), refer to the "Docker Compose Deployment" section in the **Deployment** documentation.

## Running Tests

The project includes a suite of tests located in the `tests/` directory. The following test files exist:
*   `tests/test_api.py`
*   `tests/test_models.py`
*   `tests/test_web.py`

To run all tests, you can use Python's built-in `unittest` module from the project root directory:

```bash
python -m unittest discover -s tests
```

Alternatively, if `pytest` is preferred, you can install it (`pip install pytest`) and run:

```bash
pytest
```

**Note:** Ensure your development environment (either local or Docker-based) is running and the database is initialized and accessible, as some tests may interact with the database or require running application components.

## Contribution Guidelines (Placeholder)

Currently, there are no formal contribution guidelines. If you'd like to contribute, please open an issue on the project's source repository to discuss your proposed changes or ideas.
