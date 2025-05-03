# Not_HackerNews

This is the backend API for my project Not_HackerNews. 
This is a news aggregation and discussion forum inspired by Hacker News. This API provides functionality for user authentication, post management, nested comments, and voting.

## Installation 
1. Clone this repository:
   ```bash
   git clone https://github.com/R-Yash/not_hackernews
   cd hn-inspired-forum
   ```
2. Install dependencies from requirements.txt
    ```bash
    pip install -r requiremnets.txt
    ```
3. Define All the necessary credentials and keys in the .env file

4. Start the server
    ```
    uvicorn app:app --reload
    ```

## Features

- **User Management**: Register, login, and logout functionality with JWT authentication
- **Posts**: Create, retrieve, and list posts with pagination, sorting, and search
- **Comments**: Create, update, and delete comments with nested replies support
- **Voting System**: Upvote, downvote, or remove votes on posts
- **Rate Limiting**: Basic API rate limiting protection

## Tech Stack

- **FastAPI**: A Python Library for Backend
- **PostgreSQL**: Database
- **JWT (Jose)**: JSON Web Token for Authentication
- **Passlib**: Password hashing utilities
- **SlowAPI**: Rate limiting functionality

## API Endpoints

More Information is available in `api.md`

### Authentication

- `POST /signup`: Register a new user
- `POST /login`: Log in and receive an access token
- `POST /logout`: Log out (client-side token removal)
- `GET /users`: List all registered users

### Posts

- `GET /posts`: List posts with pagination, sorting, and search
- `POST /posts`: Create a new post
- `GET /posts/{post_id}`: Get a specific post
- `POST /posts/{post_id}/vote`: Vote on a post (1, -1, or 0)

### Comments

- `GET /comments/posts/{post_id}/comments`: Get all comments for a post
- `POST /comments/posts/{post_id}/comments`: Add a comment to a post
- `PUT /comments/comments/{comment_id}`: Update a comment
- `DELETE /comments/comments/{comment_id}`: Delete a comment and its replies

## AI Tools that helped me
- ChatGPT -> I used ChatGPT for fixing bugs in my code. It also helped my write API documentation and docstrings for functions
- Github Copilot -> Copilot helped me optimize my code and make it more efficient.

## Screenshots
![image](https://github.com/user-attachments/assets/bee0412c-36d1-4d6d-aeeb-a1ff6d7f8b26)
![image](https://github.com/user-attachments/assets/2646016c-a8cf-4639-8821-741b79e5d226)
