# Guide d'Inscription - Système Amélioré

## 🎯 Fonctionnalités Implémentées

### ✅ Génération Automatique du Matricule
- Format : `ET-YYYY-NNNN` (ex: ET-2025-0001)
- Génération automatique lors de la création d'un élève
- Unique pour chaque élève
- Incrémentation automatique par année

### ✅ Formulaire Combiné d'Inscription

Le formulaire s'adapte selon le type d'inscription :

#### 1. **Nouvelle Inscription** (Élève nouveau)
- Remplir toutes les informations de l'élève (nom, prénom, date de naissance, etc.)
- Le matricule est généré automatiquement
- L'élève est créé dans la base de données
- Inscription enregistrée avec toutes les infos
- Élève assigné automatiquement à la classe

#### 2. **Réinscription** (Élève existant)
- Entrer seulement le matricule de l'élève
- Cliquer sur "Rechercher" (ou appuyer sur Entrée)
- Les informations de l'élève s'affichent automatiquement
- Remplir uniquement les détails de l'inscription (classe, montant, etc.)

## 📋 Modèle de Données

### Student (Élève)
- `matricule` : Identifiant unique auto-généré
- `name` : Nom de famille
- `first_name` : Prénom
- `surname` : Deuxième prénom (optionnel)
- `birth_date` : Date de naissance
- `email` : Email (optionnel)
- `phone` : Téléphone
- `address` : Adresse

### Enrollment (Inscription)
- `student` : Élève (lien vers Student)
- `classe` : Classe d'inscription
- `enrollment_type` : Type (inscription/réinscription)
- `academic_year` : Année scolaire (ex: 2024-2025)
- `amount` : Montant de l'inscription
- `enrollment_date` : Date d'inscription
- `status` : Statut (complétée/en attente/annulée)
- `payment_method` : Mode de paiement (optionnel)
- `reference` : Référence de transaction (optionnel)
- `notes` : Notes/remarques (optionnel)

## 🔧 Utilisation

### Pour inscrire un nouvel élève :
1. Aller sur `/finance/enrollments/create/`
2. Sélectionner "Nouvelle Inscription"
3. Remplir les informations de l'élève
4. Remplir les détails de l'inscription
5. Soumettre le formulaire
6. ✅ Le matricule est affiché dans le message de succès

### Pour réinscrire un élève existant :
1. Aller sur `/finance/enrollments/create/`
2. Sélectionner "Réinscription"
3. Entrer le matricule de l'élève (ex: ET-2025-0001)
4. Cliquer sur "Rechercher"
5. Vérifier que l'élève est trouvé
6. Remplir les détails de l'inscription (nouvelle classe, montant, etc.)
7. Soumettre le formulaire

### Voir la liste des inscriptions :
- Aller sur `/finance/enrollments/`
- Filtrer par nom, matricule, type, ou statut
- Statistiques disponibles :
  - Total des inscriptions
  - Nouvelles inscriptions
  - Réinscriptions

## 🎨 API Disponible

### GET `/finance/api/student-by-matricule/?matricule=ET-2025-0001`
Retourne les informations d'un élève par matricule (utilisé par AJAX).

**Réponse succès :**
```json
{
  "success": true,
  "student": {
    "matricule": "ET-2025-0001",
    "name": "KABORE",
    "first_name": "Jean",
    "surname": "Baptiste",
    "birth_date": "2010-05-15",
    "email": "jean@example.com",
    "phone": "+226 XX XX XX XX",
    "address": "Ouagadougou",
    "classe": "6ème A"
  }
}
```

**Réponse échec :**
```json
{
  "success": false,
  "message": "Aucun élève trouvé avec ce matricule"
}
```

## 📊 Historique des Inscriptions

Chaque inscription est enregistrée dans la table `Enrollment`, permettant de :
- Suivre l'historique complet d'un élève
- Voir toutes ses inscriptions au fil des années
- Générer des rapports sur les inscriptions par année
- Analyser les paiements d'inscription

## 🔐 Sécurité

- Tous les formulaires utilisent les tokens CSRF Django
- Validation côté serveur et client
- Champs requis marqués avec `*`
- Messages d'erreur clairs en cas de problème

## 🚀 Migrations Appliquées

```bash
python manage.py makemigrations  # ✅ Créé
python manage.py migrate         # ✅ Appliqué
```

Fichier de migration : `school_portal/migrations/0005_student_matricule_enrollment.py`

## 💡 Avantages du Système

1. **Simplicité** : Un seul formulaire pour tout
2. **Rapidité** : Réinscription en 3 clics
3. **Traçabilité** : Historique complet des inscriptions
4. **Automatisation** : Matricule généré automatiquement
5. **Flexibilité** : Fonctionne pour nouveaux élèves et réinscriptions
