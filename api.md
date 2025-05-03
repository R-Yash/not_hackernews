# API Documentation

This document outlines the available API endpoints for the FastAPI application, generated from the function docstrings. It covers authentication, posts, and comments functionalities.

---

## Authentication (`auth.py`)

Endpoints related to user signup, login, management, and token handling.

### **POST** `/signup`

* **Description**: Registers a new user in the database.
* **Request Body**: `UserCreate` schema
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```
* **Success Response**: `201 Created`
    ```json
    {
        "msg": "User created successfully"
    }
    ```
* **Error Responses**:
    * `400 Bad Request`: Username already registered.

### **POST** `/login`

* **Description**: Authenticates a user and returns an access token.
* **Request Body**: `OAuth2PasswordRequestForm` (Form data)
    * `username`: string
    * `password`: string
* **Success Response**: `200 OK` (`Token` schema)
    ```json
    {
        "access_token": "string",
        "token_type": "bearer"
    }
    ```
* **Error Responses**:
    * `401 Unauthorized`: Incorrect username or password.

### **POST** `/logout`

* **Description**: Placeholder for user logout. Currently returns a success message. (Actual logout typically involves client-side token removal).
* **Success Response**: `200 OK`
    ```json
    {
        "msg": "Logout successful"
    }
    ```

### **GET** `/users`

* **Description**: Retrieves a list of all registered usernames.
* **Success Response**: `200 OK`
    ```json
    [
        "string"
    ]
    ```

---

## Posts (`posts.py`)

Endpoints for creating, retrieving, listing, and voting on posts.

### **GET** `/posts/`

* **Description**: Lists posts with pagination, sorting, and title search.
* **Query Parameters**:
    * `skip` (int, optional, default: 0): Number of posts to skip (for pagination).
    * `limit` (int, optional, default: 10): Maximum number of posts to return.
    * `sort` (Literal["new", "top"], optional, default: "new"): Sorting criteria ('new' by creation time or 'top' by points).
    * `search` (string, optional): Optional search term to filter posts by title (case-insensitive).
* **Success Response**: `200 OK` (List of `PostSchema`)
    ```json
    [
        {
            "id": 0,
            "title": "string",
            "url": "string",
            "text": "string",
            "author": "string",
            "points": 0,
            "comment_count": 0
        }
    ]
    ```

### **POST** `/posts/`

* **Description**: Creates a new post authored by the current authenticated user.
* **Authentication**: Required (Bearer Token via `get_current_user`).
* **Request Body**: `PostCreate` schema
    ```json
    {
        "title": "string",
        "url": "string", // Optional
        "text": "string" // Optional
        // Author field is ignored, taken from token
    }
    ```
* **Success Response**: `201 Created` (`PostSchema`)
    ```json
    {
        "id": 0,
        "title": "string",
        "url": "string",
        "text": "string",
        "author": "string", // Authenticated user's username
        "points": 0,
        "comment_count": 0
    }
    ```

### **GET** `/posts/{post_id}`

* **Description**: Retrieves a single post by its ID, including its comment count.
* **Path Parameters**:
    * `post_id` (int): The ID of the post to retrieve.
* **Success Response**: `200 OK` (`PostSchema`)
    ```json
    {
        "id": 0,
        "title": "string",
        "url": "string",
        "text": "string",
        "author": "string",
        "points": 0,
        "comment_count": 0
    }
    ```
* **Error Responses**:
    * `404 Not Found`: Post not found.

### **POST** `/posts/{post_id}/vote`

* **Description**: Casts or updates a vote on a specific post by the current user.
* **Authentication**: Required (Bearer Token via `get_current_user`).
* **Path Parameters**:
    * `post_id` (int): The ID of the post to vote on.
* **Query Parameters**:
    * `vote` (int, required): Vote value: 1 for upvote, -1 for downvote, 0 to clear vote. Must be between -1 and 1.
* **Success Response**: `200 OK` (`PostSchema` - updated post)
    ```json
    {
        "id": 0,
        "title": "string",
        "url": "string",
        "text": "string",
        "author": "string",
        "points": 0, // Updated points
        "comment_count": 0 // Current comment count
    }
    ```
* **Error Responses**:
    * `404 Not Found`: Post not found.
    * `400 Bad Request`: Vote value already cast (trying to upvote when already upvoted, or downvote when already downvoted).

---

## Comments (`comments.py`)

Endpoints for managing comments on posts.

### **GET** `/posts/{post_id}/comments`

* **Description**: Retrieves all comments for a specific post, structured as a nested tree.
* **Path Parameters**:
    * `post_id` (int): The ID of the post to retrieve comments for.
* **Success Response**: `200 OK` (List of `CommentSchema`, nested)
    ```json
    [
        {
            "text": "string",
            "parent_id": 0, // null for top-level comments
            "id": 0,
            "post_id": 0,
            "author": "string",
            "children": [ // Nested CommentSchema objects
                // ...
            ]
        }
    ]
    ```
* **Error Responses**:
    * `404 Not Found`: Post not found.

### **POST** `/posts/{post_id}/comments`

* **Description**: Creates a new comment on a specific post.
* **Authentication**: Required (Bearer Token via `get_current_user`).
* **Path Parameters**:
    * `post_id` (int): The ID of the post to comment on.
* **Request Body**: `CommentCreate` schema
    ```json
    {
        "text": "string",
        "parent_id": 0 // Optional: ID of the parent comment to reply to
    }
    ```
* **Success Response**: `201 Created` (`CommentSchema`)
    ```json
    {
        "text": "string",
        "parent_id": 0,
        "id": 0,
        "post_id": 0,
        "author": "string", // Authenticated user's username
        "children": [] // Initially empty
    }
    ```
* **Error Responses**:
    * `404 Not Found`: Post not found.
    * `400 Bad Request`: Invalid `parent_id` (does not exist or belongs to a different post).

### **PUT** `/comments/{comment_id}`

* **Description**: Updates the text of an existing comment. Only the author can update.
* **Authentication**: Required (Bearer Token via `get_current_user`).
* **Path Parameters**:
    * `comment_id` (int): The ID of the comment to update.
* **Request Body**: `CommentUpdate` schema
    ```json
    {
        "text": "string"
    }
    ```
* **Success Response**: `200 OK` (`CommentSchema` - updated comment)
    ```json
    {
        "text": "string", // Updated text
        "parent_id": 0,
        "id": 0,
        "post_id": 0,
        "author": "string",
        "children": [] // Children are typically not included/updated here
    }
    ```
*