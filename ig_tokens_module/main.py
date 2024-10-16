from celery_app import capture_instagram_queries_task, print_hola_task
from tokens import load_credentials, select_least_used_credential  # Import necessary functions
from tarea2 import print_hola


# Load the credentials
credentials = load_credentials()

# Select the least used credential
username, password = select_least_used_credential(credentials)


# Send the task to Celery for execution in the background
capture_instagram_queries_task.delay(username, password)

print(f"Task sent to Celery with username: {username}")

# Enviar la tarea de imprimir 'Hola' a Celery
print_hola_task.delay()
print("Las tareas han sido enviadas a Celery.")
