# Guide de Démarrage Rapide - Système de Gestion d'École

## Félicitations ! Votre application est complète

Tous les modèles, views, URLs et templates ont été créés. Suivez ces étapes pour lancer votre système de gestion d'école.

## Étapes de Configuration

### 1. Activer l'environnement virtuel

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Créer et appliquer les migrations

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### 4. Créer un super utilisateur

```bash
python manage.py createsuperuser
```

Exemple de création :
- **Username** : admin
- **Email** : admin@ecole.bf
- **Password** : (votre mot de passe sécurisé)

### 5. Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 6. Lancer le serveur

```bash
python manage.py runserver
```

L'application sera accessible à : **http://127.0.0.1:8000**

## Première Connexion

1. Ouvrez http://127.0.0.1:8000
2. Vous serez redirigé vers la page de connexion moderne
3. Entrez vos identifiants (admin / votre mot de passe)
4. Accédez au Dashboard !

## Configuration Initiale via l'Admin

Allez sur http://127.0.0.1:8000/admin pour créer les données de base :

### 1. Créer une Année Scolaire

1. Allez dans "Année Scolaires"
2. Cliquez sur "Ajouter année scolaire"
3. Remplissez :
   - Name: 2024-2025
   - Start date: 2024-09-01
   - End date: 2025-06-30
   - Is active: ✓ (coché)
4. Enregistrez

### 2. Créer des Modes de Paiement

1. Allez dans "Modes de Paiement"
2. Ajoutez :
   - Espèces (cash)
   - Mobile Money (mobile_money)
   - Virement Bancaire (bank_transfer)
   - Chèque (check)

### 3. Créer des Types de Frais

1. Allez dans "Types de Frais"
2. Ajoutez :
   - Inscription (inscription) - 200,000 FCFA
   - Réinscription (reinscription) - 150,000 FCFA
   - Scolarité (scolarite) - 300,000 FCFA
   - Frais d'examen (examen) - 50,000 FCFA

### 4. Créer des Enseignants

1. Allez dans "Teachers"
2. Exemple :
   - Name: OUEDRAOGO
   - First name: Paul
   - Surname: André
   - Birth date: 1980-05-15
   - Email: p.ouedraogo@ecole.bf
   - Phone: +226 70 XX XX XX
3. Créez plusieurs enseignants

### 5. Créer des Matières

1. Allez dans "Subjects"
2. Exemples :
   - Mathématiques (Teacher: Paul OUEDRAOGO)
   - Français (Teacher: ...)
   - Anglais
   - Physique-Chimie
   - SVT
   - Histoire-Géographie
   - Philosophie
   - EPS

### 6. Créer des Classes

1. Allez dans "Classes"
2. Exemples :
   - Name: Terminale S1
   - Level: Terminale
   - Teacher: Paul OUEDRAOGO
   - Students: (à ajouter plus tard)
3. Créez plusieurs classes :
   - Terminale S1, S2
   - Première L1, L2
   - Seconde A, B, C

### 7. Assigner des Matières aux Classes

1. Éditez une matière
2. Dans "Classes", sélectionnez les classes concernées
3. Enregistrez

### 8. Créer des Étudiants

1. Allez dans "Students"
2. Exemple :
   - Name: KABORE
   - First name: Jean
   - Surname: Baptiste
   - Birth date: 2006-03-15
   - Email: jean.kabore@student.bf
   - Phone: +226 75 XX XX XX
   - Address: Ouagadougou, Secteur 15
3. Créez plusieurs étudiants

### 9. Assigner des Étudiants aux Classes

1. Allez dans "Classes"
2. Éditez une classe
3. Dans "Students", sélectionnez les étudiants
4. Enregistrez

### 10. Créer des Structures de Frais

1. Allez dans "Structures de Frais"
2. Exemple :
   - Academic year: 2024-2025
   - Class level: Terminale S1
   - Fee type: Scolarité
   - Amount: 300000
   - Payment frequency: Trimestriel
3. Créez pour toutes les classes

### 11. Créer des Inscriptions

1. Allez dans "Inscriptions"
2. Exemple :
   - Student: Jean KABORE
   - Academic year: 2024-2025
   - Class enrolled: Terminale S1
   - Enrollment type: Nouvelle inscription
   - Enrollment date: 2024-09-01
   - Enrollment fee: 200000
   - Status: Confirmée

### 12. Créer des Paiements

1. Allez dans "Paiements"
2. Exemple :
   - Student: Jean KABORE
   - Academic year: 2024-2025
   - Fee type: Scolarité
   - Total amount: 300000
   - Paid amount: 100000 (premier versement)
   - Payment method: Espèces
   - Payment date: Aujourd'hui
   - Period: Trimestre 1
   - Received by: Votre nom

### 13. Ajouter des Versements

1. Éditez un paiement
2. En bas, dans "Versements", cliquez sur "Ajouter un autre Versement"
3. Remplissez :
   - Installment number: 1
   - Amount: 100000
   - Payment date: Aujourd'hui
   - Payment method: Espèces

## Navigation dans l'Application

### URLs Principales

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil (redirige vers dashboard si connecté) |
| `/login/` | Page de connexion moderne |
| `/dashboard/` | Tableau de bord avec statistiques |
| `/admin/` | Interface d'administration Django |

### Module Académique

| URL | Description |
|-----|-------------|
| `/portal/students/` | Liste des étudiants |
| `/portal/classes/` | Gestion des classes |
| `/portal/teachers/` | Liste des enseignants |
| `/portal/subjects/` | Gestion des matières |
| `/portal/grades/` | Saisie et gestion des notes |
| `/portal/reports/` | Liste des bulletins |
| `/portal/reports/<id>/` | Bulletin d'un étudiant |

### Module Finance

| URL | Description |
|-----|-------------|
| `/finance/payments/` | Gestion des paiements |
| `/finance/enrollments/` | Gestion des inscriptions |
| `/finance/reports/` | Rapports financiers |
| `/finance/receipt/<id>/` | Reçu de paiement |

## Fonctionnalités Principales

### 1. Dashboard

- Statistiques en temps réel
- Graphiques des revenus
- Paiements récents
- Aperçu des classes
- Activités récentes

### 2. Gestion des Notes

1. Menu > Notes
2. Sélectionnez une classe
3. Saisissez les notes directement dans le tableau
4. Les moyennes se calculent automatiquement
5. Export Excel disponible

### 3. Bulletins de Notes

1. Menu > Bulletins ou Notes > icône bulletin
2. Le bulletin s'affiche avec :
   - Toutes les notes de l'étudiant
   - Moyenne générale calculée
   - Appréciation automatique
   - Design professionnel imprimable
3. Boutons :
   - Imprimer (pour impression directe)
   - Exporter PDF

### 4. Gestion des Paiements

1. Menu > Finance > Paiements
2. Vue complète des paiements :
   - Payés (vert)
   - Partiels (orange)
   - Impayés (rouge)
3. Filtres par statut, type, classe
4. Export Excel

### 5. Nouveau Paiement

1. Cliquez sur "Nouveau Paiement"
2. Sélectionnez l'étudiant
3. Type de paiement
4. Montants (total et versé)
5. Mode de paiement
6. Enregistrez

### 6. Versements Échelonnés

- Les versements mettent à jour automatiquement le paiement
- Suivi détaillé de chaque versement
- Calcul automatique du reste à payer

## Modèles Disponibles

### Finance

- **AcademicYear** : Années scolaires
- **FeeType** : Types de frais (10 catégories)
- **FeeStructure** : Grille tarifaire par classe
- **Enrollment** : Inscriptions/Réinscriptions
- **PaymentMethod** : Modes de paiement
- **Payment** : Paiements avec statut automatique
- **PaymentInstallment** : Versements échelonnés
- **StudentAccount** : Comptes étudiants avec solde
- **Receipt** : Reçus avec numérotation automatique

### Académique

- **Student** : Étudiants
- **Teacher** : Enseignants
- **Class** : Classes
- **Subject** : Matières
- **Assignment** : Devoirs/Évaluations
- **Mark** : Notes

## Fonctionnalités Automatiques

### Calculs Automatiques

- Montant restant à payer
- Pourcentage de paiement
- Moyennes des étudiants
- Rangs dans la classe
- Appréciation selon la moyenne

### Mises à Jour Automatiques

- Statut de paiement (pending/partial/completed)
- Année scolaire active (une seule à la fois)
- Numérotation des reçus
- Solde des comptes étudiants

### Propriétés Calculées

- `payment.remaining_amount`
- `payment.is_fully_paid`
- `payment.payment_percentage`
- `student_account.balance`
- `class.students_count()`

## Interface Admin Avancée

### Badges de Statut

- Codes couleur pour les statuts
- Barres de progression
- Indicateurs visuels

### Filtres et Recherches

- Filtres multiples
- Recherche intelligente
- Date hierarchy

### Actions Personnalisées

- Mise à jour des comptes
- Export de données
- Actions en masse

## Design Moderne

- Page de connexion élégante
- Dashboard responsive
- Sidebar avec navigation claire
- Cards avec statistiques
- Tables modernes avec hover effects
- **AUCUN emoji** - Design professionnel
- Couleurs cohérentes (Indigo/Cyan)

## Prochaines Étapes (Optionnel)

1. **Notifications**
   - Email pour paiements
   - SMS pour rappels

2. **Rapports Avancés**
   - Export PDF des bulletins
   - Statistiques détaillées
   - Graphiques personnalisés

3. **Gestion des Absences**
   - Pointage quotidien
   - Justificatifs

4. **Portail Parent**
   - Consultation des notes
   - Paiements en ligne

## Support

- **Documentation complète** : `INSTALLATION.md`
- **Guide de design** : `DESIGN_GUIDE.md`
- **Configuration URLs** : `URL_CONFIGURATION.md`

## Commandes Utiles

```bash
# Créer un superuser
python manage.py createsuperuser

# Appliquer les migrations
python manage.py migrate

# Lancer le serveur
python manage.py runserver

# Créer une app
python manage.py startapp nom_app

# Collecter les static files
python manage.py collectstatic

# Shell Python avec Django
python manage.py shell

# Vider la base de données
python manage.py flush
```

## Prêt à Commencer !

1. Activez l'environnement virtuel
2. Installez les dépendances
3. Appliquez les migrations
4. Créez le superuser
5. Lancez le serveur
6. Connectez-vous et profitez !

**Votre système de gestion d'école complet est prêt !**
