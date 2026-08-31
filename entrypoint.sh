#!/bin/bash
set -e

echo "Démarrage de l'application École..."

# Attendre PostgreSQL si activé
if [ "${USE_POSTGRES}" = "True" ]; then
    echo "⏳ Attente de PostgreSQL (${DB_HOST:-db}:${DB_PORT:-5432})..."
    while ! nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}"; do
        sleep 0.5
    done
    echo "✅ PostgreSQL prêt!"
fi

# Attendre Redis si configuré
if [ -n "$REDIS_URL" ]; then
    echo "⏳ Attente de Redis..."
    while ! nc -z redis 6379; do
        sleep 0.5
    done
    echo "✅ Redis prêt!"
fi

# Créer le répertoire de la base de données SQLite si nécessaire
if [ "${USE_POSTGRES}" != "True" ]; then
    mkdir -p /app/db
fi

# Appliquer les migrations
echo "🔄 Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "📦 Collection des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "✨ Application prête!"
exec "$@"
