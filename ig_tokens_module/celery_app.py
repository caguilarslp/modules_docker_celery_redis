from celery import Celery
import tokens  # Import the tokens.py script
from tarea2 import print_hola
import redis

# Initialize Redis connection
r = redis.Redis(host='redis', port=6379, db=0)

# Set up Celery app with Redis as broker and backend
app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# Celery task to capture Instagram queries and store tokens in Redis
@app.task
def capture_instagram_queries_task(username, password):
    # Run the task to get the tokens
    tokens_result = tokens.asyncio.run(tokens.capture_instagram_queries(username, password))
    
    # Store the tokens in Redis
    for key, value in tokens_result.items():
        r.hset('instagram_tokens', key, value)  # Store each token field in Redis
    
    # Log the tokens to verify
    print(f"Tokens stored in Redis: {tokens_result}")
    
    return tokens_result  # Celery stores the result in Redis via Celery's backend

# Tarea para imprimir 'Hola' desde tarea2.py
@app.task
def print_hola_task():
    return print_hola()  # Llamamos a la función del módulo tarea2.py





# from celery import Celery
# import tokens  # tokens impor

# # Celery & Redis setup
# app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# # Define task
# @app.task
# def capture_instagram_queries_task(username, password):
#     # Call tokens.py
#     tokens.asyncio.run(tokens.capture_instagram_queries(username, password))
