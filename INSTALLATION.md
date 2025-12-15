# Guide d'Installation - Système de Gestion d'École

## Vue d'Ensemble

Ce système de gestion d'école offre les fonctionnalités suivantes :
- Gestion financière (inscriptions, réinscriptions, paiements, versements)
- Gestion des notes et calcul automatique des moyennes
- Gestion des classes et des étudiants
- Génération et impression des bulletins de notes
- Design moderne et responsive

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Environnement virtuel Python

## Installation

### 1. Activer l'Environnement Virtuel

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Installer les Dépendances

```bash
pip install -r requirements.txt
```

Cela installera toutes les bibliothèques nécessaires :
- Django 5.0.6
- Bootstrap 5 pour l'interface
- ReportLab et WeasyPrint pour les PDFs
- openpyxl pour l'export Excel
- Et bien d'autres...

### 3. Configuration de la Base de Données

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### 4. Créer un Super Utilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte administrateur.

### 5. Collecter les Fichiers Statiques

```bash
python manage.py collectstatic --noinput
```

### 6. Lancer le Serveur de Développement

```bash
python manage.py runserver
```

L'application sera accessible à : **http://127.0.0.1:8000**

## Configuration Initiale

### 1. Accéder à l'Administration

Allez sur http://127.0.0.1:8000/admin et connectez-vous avec votre compte super utilisateur.

### 2. Créer les Données de Base

#### Enseignants
1. Allez dans "Teachers" (Enseignants)
2. Ajoutez vos enseignants avec leurs informations

#### Matières
1. Allez dans "Subjects" (Matières)
2. Créez les matières (ex: Mathématiques, Français, etc.)
3. Assignez un enseignant à chaque matière

#### Classes
1. Créez vos classes (ex: Terminale S1, Première L2, etc.)
2. Assignez un enseignant titulaire
3. Liez les matières à chaque classe

#### Étudiants
1. Ajoutez les étudiants avec leurs informations personnelles
2. Assignez-les à leurs classes respectives

### 3. Configuration Finance

Pour activer le module financier, créez les structures de frais :
- Frais d'inscription
- Frais de scolarité (par trimestre ou annuel)
- Frais de réinscription
- Autres frais

## Structure du Projet

```
ecole-main/
│
├── school_manager/          # Configuration principale Django
│   ├── settings.py         # Paramètres de l'application
│   └── urls.py             # Routes principales
│
├── main/                   # Application pour les annonces
├── school_portal/          # Application académique (étudiants, classes, notes)
├── school_finance/         # Application financière (paiements, inscriptions)
│
├── templates/              # Templates HTML
│   ├── base.html          # Template de base
│   ├── dashboard.html     # Tableau de bord
│   ├── finance/           # Templates finance
│   ├── grades/            # Templates notes et bulletins
│   ├── classes/           # Templates classes
│   └── students/          # Templates étudiants
│
├── static/                 # Fichiers statiques
│   ├── css/
│   │   └── main.css       # CSS personnalisé moderne
│   └── js/
│       └── main.js        # JavaScript
│
├── media/                  # Fichiers uploadés
├── db.sqlite3             # Base de données SQLite
├── requirements.txt       # Dépendances Python
└── manage.py              # Script de gestion Django
```

## Fonctionnalités Principales

### 1. Dashboard
- Statistiques en temps réel
- Graphiques de revenus
- Activités récentes
- Aperçu des classes

### 2. Gestion Financière
- Enregistrement des paiements
- Suivi des inscriptions/réinscriptions
- Génération de reçus
- Rapports financiers
- Export Excel

### 3. Gestion des Notes
- Saisie des notes par matière
- Calcul automatique des moyennes
- Système de coefficients
- Classement automatique

### 4. Bulletins de Notes
- Génération automatique des bulletins
- Design professionnel prêt à imprimer
- Export PDF
- Appréciations personnalisables

### 5. Gestion des Classes
- Organisation par niveaux et séries
- Affectation des enseignants
- Gestion des matières
- Suivi des effectifs

## URLs Principales

- `/admin/` - Interface d'administration Django
- `/` - Page d'accueil / Dashboard
- `/students/` - Liste des étudiants
- `/classes/` - Gestion des classes
- `/grades/` - Gestion des notes
- `/finance/payments/` - Gestion des paiements
- `/finance/enrollments/` - Inscriptions
- `/reports/` - Bulletins de notes

## Personnalisation

### Modifier les Couleurs

Éditez `static/css/main.css` et modifiez les variables CSS :

```css
:root {
    --primary: #4F46E5;        /* Couleur principale */
    --success: #10B981;        /* Vert */
    --danger: #EF4444;         /* Rouge */
    --warning: #F59E0B;        /* Orange */
}
```

### Ajouter le Logo de l'École

1. Placez votre logo dans `static/img/logo.png`
2. Modifiez le template `templates/base.html`

### Personnaliser les Bulletins

Éditez `templates/grades/report_card.html` pour personnaliser :
- En-tête avec logo et informations de l'école
- Mise en page
- Appréciations
- Signatures

## Export et Impression

### Bulletins de Notes
1. Allez sur la page des notes
2. Sélectionnez une classe
3. Cliquez sur "Générer Bulletins"
4. Imprimez directement ou exportez en PDF

### Rapports Financiers
1. Allez dans Finance > Rapports
2. Sélectionnez la période
3. Exportez en Excel ou PDF

## Développement Futur

Fonctionnalités à implémenter :
- Système de notifications par SMS/Email
- Application mobile
- Portail parents
- Gestion de la bibliothèque
- Planning des cours
- Gestion des absences
- Module RH pour les enseignants

## Support et Aide

Pour toute question ou problème :
1. Vérifiez les logs : `python manage.py runserver` affiche les erreurs
2. Consultez la documentation Django : https://docs.djangoproject.com
3. Vérifiez que toutes les dépendances sont installées

## Sécurité

### Pour la Production

1. Changez le SECRET_KEY dans settings.py
2. Mettez DEBUG = False
3. Configurez ALLOWED_HOSTS
4. Utilisez PostgreSQL au lieu de SQLite
5. Utilisez HTTPS
6. Configurez un serveur web (Nginx + Gunicorn)

```python
# settings.py pour production
DEBUG = False
ALLOWED_HOSTS = ['votre-domaine.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecole_db',
        'USER': 'votre_user',
        'PASSWORD': 'votre_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Sauvegarde

### Sauvegarder la Base de Données

```bash
# SQLite
python manage.py dumpdata > backup.json

# PostgreSQL
pg_dump ecole_db > backup.sql
```

### Restaurer

```bash
# SQLite
python manage.py loaddata backup.json

# PostgreSQL
psql ecole_db < backup.sql
```

## Mise à Jour

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Appliquer les nouvelles migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

## Dépannage

### Erreur: "Template does not exist"
- Vérifiez que TEMPLATES['DIRS'] inclut le dossier templates
- Vérifiez les chemins des templates

### Erreur: "Static files not found"
- Exécutez `python manage.py collectstatic`
- Vérifiez STATIC_URL et STATICFILES_DIRS

### Erreur de base de données
- Supprimez db.sqlite3
- Supprimez les dossiers migrations (sauf __init__.py)
- Relancez makemigrations et migrate

## Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser et de le modifier.

---

**Développé avec Django 5.0.6 et Bootstrap 5**
