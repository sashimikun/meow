---
sidebar_label: 'API Reference'
title: 'API Reference'
---

# API Reference

This section provides detailed information about the Screenshot API endpoints.

## Take Screenshot

This is the primary endpoint for capturing screenshots of web pages.

*   **HTTP Method:** `GET`
*   **URL:** `/api/take`
*   **Description:** Captures a screenshot of the specified URL. The service will navigate to the URL, render the page, and return a PNG image of the visible content.

### Request Parameters

The following query parameters are required for each request:

*   `url` (String, Required): The full URL of the web page you want to capture.
    *   Example: `https://example.com`
*   `access_key` (String, Required): Your unique API access key obtained from your user dashboard after signing up and logging in.

### Example Request

You can use `curl` or any HTTP client to make requests. Here's an example using `curl`:

```bash
curl "http://localhost:5000/api/take?url=https://example.com&access_key=YOUR_ACCESS_KEY" -o screenshot.png
```

**Note:**
*   Replace `http://localhost:5000` with the actual base URL of the deployed API service if it's different.
*   Replace `YOUR_ACCESS_KEY` with your actual access key from your dashboard.
*   The `-o screenshot.png` flag will save the output image to a file named `screenshot.png` in your current directory.

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
*   **`500 Internal Server Error`**: Indicates an unexpected issue occurred on the server while trying to process the request. This could be due to various reasons, including transient problems with the browser rendering engine.
    ```json
    {"error": "Internal server error."}
    ```
