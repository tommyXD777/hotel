FROM python:3.11

# Carpeta de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copiar todo el proyecto
COPY . .

# Puerto en el que correrá la app
EXPOSE 5000

# Comando para iniciar Gunicorn en producción
# "app:app" significa: archivo app.py → variable app = Flask(...)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "4"]
