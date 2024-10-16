from celery_app import app  # Importa la app de Celery ya configurada
import redis

# Inicializa la conexión a Redis
r = redis.Redis(host='redis', port=6379, db=0)

# Define una nueva tarea para Celery
@app.task
def test_task():
    message = "hola desde test.py con celery"
    
    # Almacena el mensaje en Redis
    r.set('test_message', message)
    
    print(message)  # Log en la consola de Celery
    return message  # Esto será almacenado en el backend de Celery (Redis en este caso)
