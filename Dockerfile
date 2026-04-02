# Utiliser Python 3.11 comme image de base
FROM python:3.11-slim

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour WeasyPrint et autres
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    netcat-traditional \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libcairo2 \
    libcairo2-dev \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier d'abord l'entrypoint et le corriger
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires (la DB SQLite est dans le dossier du projet)
RUN mkdir -p /app/staticfiles /app/media

# Exposer le port 8000
EXPOSE 8000

# Point d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]

# Commande par défaut
CMD ["gunicorn", "school_manager.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]