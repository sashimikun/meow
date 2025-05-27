# API Reference

This section provides detailed information about the Screenshot API.

## Screenshot Endpoint

The primary endpoint for capturing screenshots.

*   **Method:** `GET`
*   **Path:** `/api/take`

## Request Parameters

The following query parameters are required for each request:

*   `url` (String, Required): The full URL of the web page you want to capture (e.g., `https://example.com`).
*   `access_key` (String, Required): Your unique API access key obtained from your user dashboard after signing up.

## Example Request

You can use `curl` or any HTTP client to make requests. Here's an example using `curl`:

```bash
curl "http://localhost:5000/api/take?url=https://example.com&access_key=YOUR_ACCESS_KEY" -o screenshot.png
```

**Note:**

*   Replace `http://localhost:5000` with the actual base URL of the deployed API service if it's different.
*   Replace `YOUR_ACCESS_KEY` with your actual access key.
*   The `-o screenshot.png` flag in the example will save the output image to a file named `screenshot.png`.

## Responses

### Success Response

*   **Status Code:** `200 OK`
*   **`Content-Type:`** `image/png`
*   **Body:** The body of the response is the PNG image data of the captured web page.

### Common Error Responses

*   **`400 Bad Request`**: Indicates that one or more required parameters (`url` or `access_key`) are missing or incorrectly formatted.
    ```json
    {"error": "Missing or invalid parameters."}
    ```
*   **`401 Unauthorized`**: Indicates that the provided `access_key` is invalid, or your account has exceeded the monthly usage limit (currently 100 screenshots).
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
