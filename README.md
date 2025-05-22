# Screenshot API Service

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

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install # To install necessary browser binaries
    ```
3.  **Run the application:**
    ```bash
    export FLASK_APP=main.py
    flask run
    ```
    Or for development with auto-reload:
    ```bash
    python main.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

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
    *   Install Playwright system dependencies: These can vary by OS. For Debian-based systems, a starting point is often: `sudo apt-get install -y $(python -m playwright print-deps)` or manually installing the libraries listed by Playwright if `print-deps` isn't available or sufficient. Refer to Playwright documentation for specific OS needs.

3.  **Application Configuration:**
    *   Set the `FLASK_APP` environment variable: `export FLASK_APP=main.py`
    *   Set the `SECRET_KEY` environment variable to a strong, unique value (do not use the default one from `main.py`): `export SECRET_KEY='your_strong_random_secret_key'`

4.  **Running the Application (Production):**
    *   Use a production-grade WSGI server like Gunicorn or uWSGI instead of Flask's built-in development server.
    *   Example Gunicorn command: `gunicorn --workers 4 --bind 0.0.0.0:8000 'main:app'` (The application will listen on port 8000 on all network interfaces).

5.  **HTTPS Configuration:**
    *   **Crucial for security.** Do not run in production without HTTPS.
    *   Typically handled by a reverse proxy (e.g., Nginx, Caddy) placed in front of the WSGI server. The reverse proxy handles SSL/TLS termination.
    *   PaaS platforms often provide built-in SSL/TLS termination through their load balancers or custom domain configurations.

6.  **Process Management:**
    *   **On a VM:** Use a process manager like `systemd` (common on modern Linux) or `supervisor` to ensure the Gunicorn (or uWSGI) process restarts if it crashes and starts on boot.
    *   **On PaaS:** This is typically handled automatically by the platform.
