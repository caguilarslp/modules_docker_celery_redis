# Usa Python 3.12 como imagen base
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia todos los archivos a la carpeta de trabajo
COPY . .

# Instala las dependencias necesarias para Playwright y el navegador Chromium
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libdrm2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instala los navegadores de Playwright
RUN playwright install chromium

# Configura permisos para que los archivos puedan ser escritos
RUN chmod -R 777 /app

# Exponer el puerto de Redis para la comunicación
EXPOSE 6379

# Comando para correr Celery en modo worker
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]



# # Usa Python 3.12 como imagen base
# FROM python:3.12-slim

# # Establece el directorio de trabajo
# WORKDIR /app

# # Copia todos los archivos a la carpeta de trabajo
# COPY . .

# # Instala las dependencias necesarias para Playwright y el navegador Chromium
# RUN apt-get update && apt-get install -y \
#     libnss3 \
#     libatk-bridge2.0-0 \
#     libgtk-3-0 \
#     libx11-xcb1 \
#     libdrm2 \
#     libgbm1 \
#     libxkbcommon0 \
#     libasound2 \
#     wget \
#     && rm -rf /var/lib/apt/lists/*

# # Instala las dependencias de Python
# RUN pip install --upgrade pip
# RUN pip install playwright

# # Instala los navegadores de Playwright
# RUN playwright install chromium

# # Configura permisos para que los archivos puedan ser escritos
# RUN chmod -R 777 /app

# # Ejecuta el script
# CMD ["python", "tokens.py"]
