
# API Authentication Documentation

## Overview

This document explains how to use authentication in the API using **JWT (JSON Web Tokens)**. We use **Access Tokens** for secure access to the API, and **Refresh Tokens** to refresh the expired access tokens.

## Authentication Flow

### 1. **Login (Get Access and Refresh Tokens)**

To get the access token and refresh token, send a POST request to the `/api/token/` endpoint with the user’s credentials.

#### Request:

```http
POST /api/token/
Content-Type: application/json
```

**Request Body:**

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

#### Response:

```json
{
    "access": "access_token_here",
    "refresh": "refresh_token_here"
}
```

- **access:** The access token used for accessing protected endpoints.
- **refresh:** The refresh token used to get a new access token when the current one expires.

### 2. **Making Authenticated Requests**

Once you have the access token, you can use it to make authenticated API requests. You need to include the **access token** in the `Authorization` header of your requests.

#### Example Request:

```http
GET /api/protected-endpoint/
Authorization: Bearer access_token_here
```

- **Authorization:** Bearer `<access_token>` – Use the access token to authenticate the request.

### 3. **Handling Token Expiry**

Access tokens have a short lifespan, so once the access token expires, you will receive a `401 Unauthorized` response indicating the token is invalid.

#### Example Response (Token Expired):

```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is expired"
        }
    ]
}
```

### 4. **Refreshing the Access Token**

When the access token expires, you can use the **refresh token** to get a new access token. Send a POST request to the `/api/token/refresh/` endpoint with the refresh token.

#### Request:

```http
POST /api/token/refresh/
Content-Type: application/json
```

**Request Body:**

```json
{
    "refresh": "refresh_token_here"
}
```

#### Response:

```json
{
    "access": "new_access_token_here"
}
```

- **access:** The new access token to use for future requests.

### 5. **Storing Tokens Securely**

Both the **access token** and **refresh token** should be securely stored in the app. Use secure storage options, such as:

- **iOS:** Keychain
- **Android:** EncryptedSharedPreferences

Do not store tokens in plain text or insecure storage.

### 6. **Token Expiry and Refresh**

- The **access token** expires after a short period (usually 15 minutes).
- The **refresh token** is used to get a new **access token** when the current one expires. Refresh tokens are long-lived but will eventually expire or be revoked.
- If the **refresh token** expires, the user will need to log in again to get new tokens.

### 7. **Logout and Token Revocation**

To log out a user and revoke their tokens, you should delete or invalidate the refresh token on the server-side. This will prevent the user from using the refresh token to generate new access tokens.

---

## Example Usage in the App

1. **Login** – When the user logs in, the app sends their credentials to `/api/token/` and stores the access and refresh tokens securely.
2. **Making Requests** – When the app needs to make a request to a protected endpoint, it includes the access token in the `Authorization` header.
3. **Token Expiry** – When the access token expires, the app sends the refresh token to `/api/token/refresh/` to get a new access token.
4. **Token Storage** – The app stores the access and refresh tokens in secure storage (e.g., Keychain or EncryptedSharedPreferences).
5. **Logging Out** – To log out, the app deletes the tokens and prevents further access.

---

## API Endpoints

### 1. **/api/token/**

- **POST:** Use this endpoint to log in and get the access and refresh tokens.
- **Request body:** `{"username": "your_username", "password": "your_password"}`
- **Response:** `{"access": "access_token_here", "refresh": "refresh_token_here"}`

### 2. **/api/token/refresh/**

- **POST:** Use this endpoint to refresh the access token using the refresh token.
- **Request body:** `{"refresh": "refresh_token_here"}`
- **Response:** `{"access": "new_access_token_here"}`

---

## Error Handling

### 1. **Token Expired**

If the access token is expired, the server will return a `401 Unauthorized` response with a message indicating the token is expired.

```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is expired"
        }
    ]
}
```

### 2. **Invalid Token**

If an invalid or incorrect token is provided, the server will return a `401 Unauthorized` response.

```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

## Security Considerations

- Always store **access tokens** and **refresh tokens** securely.
- Use **HTTPS** for all API requests to ensure the tokens are not intercepted.
- Implement token revocation if needed to log out users and invalidate tokens.
- Limit the lifetime of access tokens to reduce the impact of stolen tokens.
