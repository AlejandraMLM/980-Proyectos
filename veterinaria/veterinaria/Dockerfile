# Usa una imagen base de Python estable
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Instala dependencias del sistema necesarias para psycopg2 y el cliente PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala las dependencias de Python
# (asegúrate de que el archivo requirements.txt esté en la raíz del proyecto)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código fuente del proyecto dentro del contenedor
COPY . .

# Expone el puerto que usará Django
EXPOSE 8000

# Comando para aplicar migraciones y luego levantar el servidor de desarrollo
# (puedes cambiarlo a gunicorn si lo usarás en producción)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]




