# API Documentation

This document provides the API documentation for the Suoke Life application.

## Base URL

The base URL for all API requests is:

```
http://localhost:8080/api/v1
```

## Authentication

All API endpoints require authentication. You can use the following methods:

-   **JWT Token:** Send the token in the `Authorization` header as `Bearer <token>`.

## Endpoints

### User Service

#### `POST /users/register`

-   **Description:** Registers a new user.
-   **Request Body:**
    ```json
    {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "password": "password123"
    }
    ```
-   **Response:**
    ```json
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@example.com"
    }
    ```

#### `POST /users/login`

-   **Description:** Logs in an existing user.
-   **Request Body:**
    ```json
    {
      "email": "john.doe@example.com",
      "password": "password123"
    }
    ```
-   **Response:**
    ```json
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```

#### `GET /users/profile`

-   **Description:** Gets the user profile.
-   **Headers:**
    ```
    Authorization: Bearer <token>
    ```
-   **Response:**
    ```json
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@example.com"
    }
    ```

### Health Service

#### `GET /health/records`

-   **Description:** Gets the user's health records.
-   **Headers:**
    ```
    Authorization: Bearer <token>
    ```
-   **Response:**
    ```json
    [
      {
        "id": 1,
        "date": "2024-07-26",
        "heart_rate": 72,
        "sleep_hours": 8
      }
    ]
    ```

#### `POST /health/records`

-   **Description:** Creates a new health record.
-   **Request Body:**
    ```json
    {
      "date": "2024-07-26",
      "heart_rate": 72,
      "sleep_hours": 8
    }
    ```
-   **Headers:**
    ```
    Authorization: Bearer <token>
    ```
-   **Response:**
    ```json
    {
      "id": 2,
      "date": "2024-07-26",
      "heart_rate": 72,
      "sleep_hours": 8
    }
    ```

### LLM Service

#### `POST /llm/generate`

-   **Description:** Generates text using the LLM.
-   **Request Body:**
    ```json
    {
      "prompt": "What is the meaning of life?"
    }
    ```
-   **Response:**
    ```json
    {
      "text": "The meaning of life is..."
    }
    ```

### Life Service

#### `GET /life/records`

-   **Description:** Gets the user's life records.
-   **Headers:**
    ```
    Authorization: Bearer <token>
    ```
-   **Response:**
    ```json
    [
      {
        "id": 1,
        "date": "2024-07-26",
        "activity": "Morning walk",
        "duration": "30 minutes"
      }
    ]
    ```

#### `POST /life/records`

-   **Description:** Creates a new life record.
-   **Request Body:**
    ```json
    {
      "date": "2024-07-26",
      "activity": "Morning walk",
      "duration": "30 minutes"
    }
    ```
-   **Headers:**
    ```
    Authorization: Bearer <token>
    ```
-   **Response:**
    ```json
    {
      "id": 2,
      "date": "2024-07-26",
      "activity": "Morning walk",
      "duration": "30 minutes"
    }
    ```

## Error Handling

The API returns standard HTTP status codes:

-   `200 OK`: Success
-   `201 Created`: Resource created
-   `400 Bad Request`: Invalid request
-   `401 Unauthorized`: Authentication failed
-   `404 Not Found`: Resource not found
-   `500 Internal Server Error`: Server error 