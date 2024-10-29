from celery import Celery
import tokens  # Importa el módulo tokens.py
import redis
import asyncio  # Importa asyncio directamente
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Inicializar conexión Redis
try:
    r = redis.Redis(host='redis', port=6379, db=0)
except Exception as e:
    logging.error(f"Error al conectar con Redis: {e}")
    raise e

# Configurar la aplicación Celery con Redis como broker y backend
app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# Tarea de Celery para capturar consultas de Instagram y almacenar tokens en Redis
@app.task
def capture_instagram_queries_task(username, password):
    try:
        # Crear instancia de TokenManager
        token_manager = tokens.TokenManager()

        # Ejecutar el método asíncrono para obtener los tokens
        tokens_result = asyncio.run(token_manager.capture_instagram_queries(username, password))

        # Almacenar los tokens en Redis
        for key, value in tokens_result.items():
            r.hset('instagram_tokens', key, value)  # Almacenar cada campo de token en Redis

        # Registrar los tokens para verificar
        logging.info(f"Tokens almacenados en Redis: {tokens_result}")

        return tokens_result  # Celery almacena el resultado en Redis a través del backend de Celery
    except Exception as e:
        logging.error(f"Ocurrió un error en la tarea de Celery: {e}")
        raise e
