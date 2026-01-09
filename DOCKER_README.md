# 🐳 Déploiement Docker - Système de Gestion Scolaire

## 📋 Prérequis

- Docker Desktop installé (Windows/Mac) ou Docker Engine (Linux)
- Docker Compose (inclus dans Docker Desktop)
- Au moins 2GB de RAM disponible

## 🚀 Démarrage Rapide

### Option 1 : Version Simple (Recommandée pour débuter)

Cette version lance uniquement l'application Django avec SQLite :

```bash
# Construire et démarrer
docker-compose -f docker-compose.simple.yml up --build

# Accéder à l'application
http://localhost:8000
```

### Option 2 : Version Complète (Production)

Cette version inclut Redis, Celery, et Nginx :

```bash
# Construire et démarrer tous les services
docker-compose up --build

# Accéder à l'application via Nginx
http://localhost
```

## 📦 Services Disponibles

### docker-compose.simple.yml
- **web** : Application Django avec Gunicorn (port 8000)

### docker-compose.yml (complet)
- **web** : Application Django avec Gunicorn (port 8000)
- **redis** : Cache et broker pour Celery (port 6379)
- **celery** : Worker pour tâches asynchrones
- **celery-beat** : Scheduler pour tâches planifiées
- **nginx** : Serveur web reverse proxy (ports 80/443)

## 🛠️ Commandes Utiles

### Gestion des conteneurs

```bash
# Démarrer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f web

# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Commandes Django dans Docker

```bash
# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Effectuer les migrations
docker-compose exec web python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic

# Accéder au shell Django
docker-compose exec web python manage.py shell

# Accéder au shell du conteneur
docker-compose exec web bash
```

### Gestion de la base de données

```bash
# Sauvegarder la base de données SQLite
docker cp ecole_web:/app/db.sqlite3 ./backup_$(date +%Y%m%d).sqlite3

# Restaurer une sauvegarde
docker cp ./backup.sqlite3 ecole_web:/app/db.sqlite3
docker-compose restart web
```

## 🔧 Configuration

### Variables d'environnement

Copiez `.env.example` vers `.env` et modifiez les valeurs :

```bash
cp .env.example .env
```

Principales variables à configurer :
- `SECRET_KEY` : Clé secrète Django (générer une nouvelle pour production)
- `DEBUG` : False en production
- `ALLOWED_HOSTS` : Votre domaine (ex: ecole.example.com)

### Configuration Nginx (Production)

Le fichier `nginx/nginx.conf` contient la configuration du serveur web.
Modifiez `server_name` pour votre domaine :

```nginx
server_name votre-domaine.com www.votre-domaine.com;
```

## 📊 Volumes Docker

Les données persistantes sont stockées dans des volumes Docker :

- `db_volume` : Base de données SQLite
- `static_volume` : Fichiers statiques (CSS, JS, images)
- `media_volume` : Fichiers uploadés (logos, documents)

### Lister les volumes
```bash
docker volume ls
```

### Inspecter un volume
```bash
docker volume inspect ecole-main_db_volume
```

## 🔒 Sécurité en Production

1. **Changez la SECRET_KEY** :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Désactivez DEBUG** :
```
DEBUG=False
```

3. **Configurez ALLOWED_HOSTS** :
```
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
```

4. **Utilisez HTTPS** :
- Installez un certificat SSL (Let's Encrypt recommandé)
- Configurez Nginx pour SSL

## 🐛 Dépannage

### Problème : Port déjà utilisé
```bash
# Changer le port dans docker-compose.yml
ports:
  - "8080:8000"  # Au lieu de 8000:8000
```

### Problème : Permissions sur entrypoint.sh
```bash
chmod +x entrypoint.sh
docker-compose build --no-cache
```

### Problème : Base de données verrouillée
```bash
# Redémarrer les services
docker-compose restart

# Si le problème persiste, recréer les conteneurs
docker-compose down
docker-compose up
```

### Voir les logs détaillés
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f web
docker-compose logs -f celery
```

## 📈 Monitoring

### Vérifier l'état des services
```bash
docker-compose ps
```

### Statistiques de ressources
```bash
docker stats
```

## 🔄 Mise à jour

```bash
# Récupérer les dernières modifications
git pull

# Reconstruire les images
docker-compose build

# Redémarrer les services
docker-compose up -d

# Appliquer les migrations
docker-compose exec web python manage.py migrate
```

## 📝 Structure des fichiers Docker

```
.
├── Dockerfile                    # Image Docker de l'application
├── docker-compose.yml           # Configuration complète (production)
├── docker-compose.simple.yml    # Configuration simplifiée (dev)
├── entrypoint.sh                # Script de démarrage
├── .dockerignore                # Fichiers à exclure de l'image
├── .env.example                 # Variables d'environnement exemple
└── nginx/
    └── nginx.conf               # Configuration Nginx
```

## 🆘 Support

En cas de problème :
1. Vérifiez les logs : `docker-compose logs -f`
2. Vérifiez l'état des services : `docker-compose ps`
3. Consultez la documentation Docker : https://docs.docker.com
4. Consultez la documentation Django : https://docs.djangoproject.com

## 📚 Ressources

- [Documentation Docker](https://docs.docker.com/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Best Practices Django + Docker](https://docs.docker.com/samples/django/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
