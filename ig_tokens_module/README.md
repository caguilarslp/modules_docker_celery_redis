# Instagram Token Extraction - Demo

This project is a demonstration of automating the process of logging into Instagram using credentials stored in a JSON file, generating session tokens, and storing them both in Redis and in a local file. Celery is used to run tasks in the background, and Redis is used as the broker and result storage.

## Prerequisites

Before compiling and running the project, make sure you have the following installed:

- Docker
- Docker Compose

## Project Structure

- **`tokens.py`**: Main script responsible for logging into Instagram, generating session tokens, and storing them.
- **`celery_app.py`**: Contains the Celery configuration and task logic for running the process in the background.
- **`main.py`**: Entry point to send the task to Celery.
- **`credentials.json`**: File containing Instagram credentials.
- **`requirements.txt`**: Dependencies required to run the project.
- **`Dockerfile`**: Docker configuration to build the image.
- **`docker-compose.yml`**: Docker Compose configuration to start the Redis and Celery services.

## Credentials Setup

You need to create and configure a `credentials.json` file in the root of the project. This file should have the following format:

```json
{
    "instagram_credentials": [
        {
            "username_session": "your_username1",
            "password": "your_password1",
            "used_count": 0,
            "last_used": false
        },
        {
            "username_session": "your_username2",
            "password": "your_password2",
            "used_count": 0,
            "last_used": false
        }
    ]
}
```

Replace `your_username1`, `your_password1`, etc., with your actual Instagram credentials. These credentials will be used to log in and generate session tokens.

## What does the project do?

1. **Retrieve credentials**: The script reads credentials from the `credentials.json` file and selects the least used one.
2. **Generate tokens**: It logs into Instagram using the selected credentials and generates session tokens (such as `csrf_token`, `session_id`, and `ds_user_id`).
3. **Store tokens**: The tokens are stored in both:
   - **Redis** under the key `instagram_tokens`.
   - **`tokens_cache.json`** file for local storage.

## How to Compile and Run

### 1. Build the Docker containers

First, build the Docker containers using Docker Compose:

```bash
docker-compose up --build
```

This will start the Redis service, the Celery worker, and the application container.

### 2. Execute the script

To execute the script and send a task to Celery, you need to access the container where the application is running (likely `worker-1`):

1. List the running containers to confirm the name of the container:

   ```bash
   docker ps
   ```

2. Connect to the container running the worker (e.g., `tokens_module-worker-1`):

   ```bash
   docker exec -it tokens_module-worker-1 /bin/bash
   ```

3. Run `main.py` inside the container to send a task to Celery:

   ```bash
   python main.py
   ```

This will send a task to the Celery worker, which will log into Instagram and generate the session tokens.

### 3. View stored tokens in Redis

To view the tokens stored in Redis:

1. Connect to the Redis container (e.g., `tokens_module-redis-1`):

   ```bash
   docker exec -it tokens_module-redis-1 redis-cli
   ```

2. List all keys stored in Redis:

   ```bash
   KEYS *
   ```

3. View the content of the `instagram_tokens` key:

   ```bash
   HGETALL instagram_tokens
   ```

This will display the tokens that were generated and stored by the script.

## Important Notes

- This demo currently retrieves credentials from a JSON file and generates Instagram session tokens, which are then stored in Redis and in a local file.
- Make sure to use your own credentials in the `credentials.json` file for the script to work.
  