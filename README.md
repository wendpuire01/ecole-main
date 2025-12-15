# 🏫 Système de Gestion d'École

Application web complète de gestion d'établissement scolaire développée avec Django 5.0.6

## 📋 Fonctionnalités

### 🎓 Gestion Académique
- **Étudiants** : Création, modification, profils détaillés
- **Enseignants** : Gestion du corps enseignant
- **Classes** : Organisation des classes par niveau
- **Matières** : Gestion des matières avec coefficients

### 📊 Gestion des Notes
- **Saisie des notes** : Interface intuitive avec modale
- **Calcul automatique** : Moyennes avec coefficients
- **Trimestres/Semestres** : Gestion des périodes scolaires
- **Bulletins** : Génération et impression
- **Classements** : Rangs automatiques par classe

### 💰 Gestion Financière
- **Inscriptions** : Gestion des inscriptions et ré-inscriptions
- **Paiements** : Suivi des versements et scolarité
- **Factures** : Génération automatique des reçus
- **Rapports** : États financiers

### 📈 Tableaux de Bord
- **Dashboard général** : Vue d'ensemble
- **Statistiques** : Effectifs, moyennes, taux de réussite
- **Graphiques** : Visualisations Chart.js

## 🚀 Installation Rapide

### 1. Cloner le projet
```bash
git clone https://github.com/wendpuire01/ecole-main.git
cd ecole-main
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations
```bash
python manage.py migrate
```

### 5. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

### 7. Accéder à l'application
- **Application** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/
- **Dashboard** : http://127.0.0.1:8000/dashboard/

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Démarrage rapide
- **[QUICK_START_NOTES.md](QUICK_START_NOTES.md)** - Guide système de notes
- **[GUIDE_GESTION_NOTES.md](GUIDE_GESTION_NOTES.md)** - Guide complet notes
- **[INSTALLATION.md](INSTALLATION.md)** - Installation détaillée
- **[DESIGN_GUIDE.md](DESIGN_GUIDE.md)** - Guide de design
- **[URL_CONFIGURATION.md](URL_CONFIGURATION.md)** - Configuration URLs

## 🛠️ Technologies

- **Framework** : Django 5.0.6
- **Base de données** : SQLite (développement)
- **Frontend** : Bootstrap 5, FontAwesome 6
- **Charts** : Chart.js
- **PDF** : ReportLab, WeasyPrint
- **Export** : openpyxl (Excel)

## 📁 Structure du Projet

```
ecole-main/
├── main/                   # App principale (auth, dashboard)
├── school_portal/          # App gestion scolaire
├── school_finance/         # App gestion financière
├── school_manager/         # Configuration Django
├── static/                 # CSS, JS, Images
├── templates/              # Templates HTML
└── venv/                   # Environnement virtuel
```

## 🎯 URLs Principales

| Fonctionnalité | URL |
|---------------|-----|
| Dashboard | `/dashboard/` |
| Classes | `/portal/classes/` |
| Étudiants | `/portal/students/` |
| Enseignants | `/portal/teachers/` |
| Matières | `/portal/subjects/` |
| Notes | `/portal/grades/` |
| Bulletins | `/portal/reports/` |
| Finance | `/finance/` |
| Admin | `/admin/` |

## ⚙️ Configuration

### Base de données
Par défaut : SQLite (`db.sqlite3`)

Pour PostgreSQL/MySQL, modifier `school_manager/settings.py` :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecole_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Fichiers statiques
```bash
python manage.py collectstatic
```

## 🔑 Fonctionnalités Clés

### Système de Notes
- Types d'évaluations : Devoir, Composition, Interrogation, Examen, TP
- Coefficients par matière et par évaluation
- Calcul automatique des moyennes
- Rangs dans la classe
- Appréciations automatiques

### Formule de Calcul
```
Moyenne_Générale = Σ(Moyenne_Matière × Coefficient_Matière) / Σ(Coefficients)
```

## 👥 Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

**Wendpuiré KABORE**
- GitHub: [@wendpuire01](https://github.com/wendpuire01)

## 🙏 Remerciements

- Django Framework
- Bootstrap Team
- FontAwesome
- Communauté Open Source

---

**Version:** 2.0
**Dernière mise à jour:** Décembre 2025


