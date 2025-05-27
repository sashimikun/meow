# Frontend Overview

The service provides a web interface for user account management and API key retrieval. This interface allows users to sign up for the service, log in to their accounts, and access their API key.

<!-- TODO: Add screenshots of the web interface here -->

## User Registration (Sign Up)

New users can create an account to access the Screenshot API service. The registration process typically involves providing an email address and creating a password.

The user interface for registration is rendered from the `signup.html` template.

<!-- TODO: Add screenshot of the Sign Up page here -->

## User Login (Sign In)

Existing users can log in to their accounts using their registered email address and password.

The user interface for logging in is rendered from the `signin.html` template.

<!-- TODO: Add screenshot of the Sign In page here -->

## Dashboard

After successfully logging in, users are directed to their personal dashboard. The primary purpose of the dashboard is to display the user's unique `access_key`, which is required to use the API.

The dashboard may also display information about the user's API usage, such as the number of screenshots taken in the current billing cycle (e.g., "Usage tracking (100 screenshots per user per month)").

The user interface for the dashboard is rendered from the `dashboard.html` template.

<!-- TODO: Add screenshot of the Dashboard page here -->

## Landing Page (Index)

The `index.html` template serves as the main landing page for the service. It likely provides a general overview of the Screenshot API, its features, and includes links or buttons for users to either sign up for a new account or sign in to an existing one.

<!-- TODO: Add screenshot of the Landing page here -->
