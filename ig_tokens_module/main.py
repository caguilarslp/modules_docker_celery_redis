from celery_app import capture_instagram_queries_task
from tokens import TokenManager  # Importar la clase TokenManager

# Crear una instancia de TokenManager
token_manager = TokenManager()

# Cargar las credenciales usando el método de la clase
credentials = token_manager.load_credentials()

# Seleccionar la credencial menos usada usando el método de la clase
username, password = token_manager.select_least_used_credential(credentials)

# Enviar la tarea a Celery para ejecución en segundo plano
capture_instagram_queries_task.delay(username, password)

print(f"Task sent to Celery with username: {username}")


#
# from celery_app import capture_instagram_queries_task
# from tokens import TokenManager  # Importar la clase TokenManager

# # Crear una instancia de TokenManager
# token_manager = TokenManager()

# # Cargar las credenciales usando el método de la clase
# credentials = token_manager.load_credentials()

# # Seleccionar la credencial menos usada usando el método de la clase
# username, password = token_manager.select_least_used_credential(credentials)

# # Enviar la tarea a Celery para ejecución en segundo plano
# capture_instagram_queries_task.delay(username, password)

# print(f"Task sent to Celery with username: {username}")



# from celery_app import capture_instagram_queries_task
# #from tokens import load_credentials, select_least_used_credential  # Import necessary functions
# from tokens import TokenManager  # Importar la clase TokenManager

# # Crear una instancia de TokenManager
# token_manager = TokenManager()

# # Load the credentials
# credentials = load_credentials()

# # Select the least used credential
# username, password = select_least_used_credential(credentials)

# # Send the task to Celery for execution in the background
# capture_instagram_queries_task.delay(username, password)

# print(f"Task sent to Celery with username: {username}")
