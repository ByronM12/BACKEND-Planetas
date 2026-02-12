#!/bin/bash
set -e

# Aplicar migraciones de la base de datos
echo "Aplicando migraciones de la base de datos..."
alembic upgrade head

# Iniciar el servidor con Gunicorn
echo "Iniciando servidor..."
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app