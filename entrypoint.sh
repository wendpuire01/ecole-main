#!/bin/bash

# Script d'entrée pour Docker avec SQLite
# Ce script s'exécute avant le démarrage de l'application

set -e

echo "Démarrage de l'application École..."

# Attendre que Redis soit prêt (optionnel)
if [ -n "$REDIS_URL" ]; then
    echo "⏳ Attente de Redis..."
    while ! nc -z redis 6379; do
      sleep 0.1
    done
    echo "✅ Redis prêt!"
fi

# Créer le répertoire de la base de données si nécessaire
mkdir -p /app/db

# Effectuer les migrations
echo "🔄 Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "📦 Collection des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# Créer un superutilisateur si nécessaire (optionnel - décommenter si besoin)
# echo "👤 Création du superutilisateur..."
# python manage.py shell << END
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@ecole.bf', 'admin123')
#     print('✅ Superutilisateur créé: admin/admin123')
# else:
#     print('ℹ️  Superutilisateur existe déjà')
# END

echo "✨ Application prête à démarrer!"

# Exécuter la commande passée en argument
exec "$@"
