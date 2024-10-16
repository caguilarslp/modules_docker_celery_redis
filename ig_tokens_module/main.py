from celery_app import capture_instagram_queries_task
from tokens import load_credentials, select_least_used_credential  # Import necessary functions

# Load the credentials
credentials = load_credentials()

# Select the least used credential
username, password = select_least_used_credential(credentials)

# Send the task to Celery for execution in the background
capture_instagram_queries_task.delay(username, password)

print(f"Task sent to Celery with username: {username}")
