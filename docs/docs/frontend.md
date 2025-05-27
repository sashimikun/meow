---
sidebar_label: 'Web Interface'
title: 'Web Interface & User Guide'
---

# Web Interface & User Guide

This document provides an overview of the web interface for the Screenshot API Service, guiding you through user account management and API key retrieval.

## Overview

The web interface serves as the primary portal for users to manage their accounts and access their unique API key. This key is essential for authenticating requests to the screenshot API. The interface provides a simple way to sign up, sign in, and view your API credentials.

## User Registration

To begin using the Screenshot API Service, you must first create an account.

1.  **Navigate to the Signup Page:** Access the web portal (e.g., `http://localhost:5000/` or the production URL) and find the "Sign Up" or "Register" link. This will typically lead you to a URL like `/signup`.
2.  **Provide Registration Details:** You will need to fill out a registration form. This usually includes:
    *   Your email address
    *   A chosen password
    *   Password confirmation
3.  **Submit the Form:** After filling in the required information, submit the form to create your account.

*(Note: A screenshot of the signup page would be beneficial here.)*

## Sign-in Process

Once your account is registered, you can sign in to access your dashboard.

1.  **Navigate to the Sign-in Page:** From the web portal's main page, find the "Sign In" or "Login" link. This will typically lead you to a URL like `/signin`.
2.  **Enter Credentials:** Provide the email address and password you used during registration.
3.  **Submit:** Click the "Sign In" button.

*(Note: A screenshot of the sign-in page would be beneficial here.)*

## Dashboard

After successfully signing in, you will be redirected to your user dashboard.

*   **API Key Display:** The primary purpose of the dashboard is to display your unique `access_key`. This key is required for all API requests. You can copy this key directly from the dashboard.
*   **Usage Information:** The dashboard may also display information about your current API usage, such as the number of screenshots taken in the current billing cycle and your monthly quota.
*   **Account Management:** Depending on the service's features, the dashboard might offer options to change your password or manage other account settings.

*(Note: A screenshot of the dashboard, highlighting the API key location, would be beneficial here.)*

Ensure you keep your `access_key` confidential, as it is used to authenticate your API requests and track your usage. If you suspect your key has been compromised, you should look for options to regenerate it or contact support.
