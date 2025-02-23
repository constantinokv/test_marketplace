#!/bin/bash

# Script para crear estructura de directorios para Marketplace Analysis

# Directorio raíz
PROJECT_ROOT="marketplace_analysis"

# Crear estructura de directorios
mkdir -p $PROJECT_ROOT/app/api
mkdir -p $PROJECT_ROOT/app/core
mkdir -p $PROJECT_ROOT/app/services
mkdir -p $PROJECT_ROOT/data/raw
mkdir -p $PROJECT_ROOT/data/processed
mkdir -p $PROJECT_ROOT/models/trained
mkdir -p $PROJECT_ROOT/tests

# Crear archivos __init__.py vacíos
touch $PROJECT_ROOT/app/__init__.py
touch $PROJECT_ROOT/app/api/__init__.py
touch $PROJECT_ROOT/app/core/__init__.py
touch $PROJECT_ROOT/app/services/__init__.py
touch $PROJECT_ROOT/tests/__init__.py

# Crear archivos de código base
touch $PROJECT_ROOT/app/api/routes.py
touch $PROJECT_ROOT/app/api/models.py
touch $PROJECT_ROOT/app/core/config.py
touch $PROJECT_ROOT/app/core/security.py
touch $PROJECT_ROOT/app/services/analyzer.py
touch $PROJECT_ROOT/app/services/recommender.py

# Crear archivo CSV de ejemplo en data/raw
echo "product_id,name,category,price" > $PROJECT_ROOT/data/raw/products.csv

# Crear .gitignore
cat << EOF > $PROJECT_ROOT/.gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*\$py.class

# Virtual environment
venv/
env/
.env

# IDE settings
.vscode/
.idea/

# Logs
*.log

# Model files
*.pkl

# Jupyter Notebook
.ipynb_checkpoints/

# Otros archivos temporales
.DS_Store
EOF

# Crear requirements.txt
cat << EOF > $PROJECT_ROOT/requirements.txt
fastapi==0.95.1
uvicorn==0.22.0
pydantic==1.10.7
scikit-learn==1.2.2
pandas==2.0.1
numpy==1.24.3
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
pytest==7.3.1
EOF

# Crear Dockerfile
cat << EOF > $PROJECT_ROOT/Dockerfile
# Usar imagen base de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "Estructura de directorios creada exitosamente en $PROJECT_ROOT"