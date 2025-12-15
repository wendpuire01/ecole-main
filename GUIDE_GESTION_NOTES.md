# Guide Complet - Système de Gestion des Notes

## Vue d'ensemble du système

Le système de gestion des notes permet de :
- Gérer les périodes scolaires (trimestres/semestres)
- Assigner des étudiants aux classes
- Définir des coefficients par matière et par classe
- Saisir des notes avec différents types d'évaluations
- Calculer automatiquement les moyennes
- Générer des bulletins de notes

---

## FLOW COMPLET - Étape par Étape

### ÉTAPE 1 : Configuration Initiale (Admin Django)

#### 1.1 Créer une Période Scolaire
**URL:** http://127.0.0.1:8000/admin/school_portal/period/

1. Cliquez sur "Ajouter période"
2. Remplissez :
   - **Name:** Choisir "1er Trimestre" (ou 2e, 3e)
   - **Academic year:** Ex: 2024-2025
   - **Start date:** Date de début du trimestre
   - **End date:** Date de fin du trimestre
   - **Is active:** Cocher pour marquer comme période active
3. Cliquez sur "Enregistrer"

**Note:** Une seule période peut être active à la fois.

---

#### 1.2 Créer des Enseignants
**URL:** http://127.0.0.1:8000/portal/teachers/create/

1. Cliquez sur "Nouvel Enseignant"
2. Remplissez tous les champs obligatoires
3. Cliquez sur "Enregistrer"

---

#### 1.3 Créer des Matières
**URL:** http://127.0.0.1:8000/portal/subjects/create/

1. Cliquez sur "Nouvelle Matière"
2. Remplissez :
   - **Nom de la Matière:** Ex: Mathématiques
   - **Enseignant:** Sélectionner un enseignant (optionnel)
3. Cliquez sur "Enregistrer"

**Matières recommandées à créer:**
- Mathématiques
- Français
- Anglais
- Sciences Physiques
- SVT (Sciences de la Vie et de la Terre)
- Histoire-Géographie
- EPS (Éducation Physique et Sportive)

---

#### 1.4 Créer des Classes
**URL:** http://127.0.0.1:8000/portal/classes/

1. Cliquez sur "Nouvelle Classe"
2. Remplissez dans la modale :
   - **Nom de la Classe:** Ex: 3ème A
   - **Niveau:** Sélectionner (6ème, 5ème, etc.)
   - **Enseignant Titulaire:** Sélectionner (optionnel)
   - **Matières:** Sélectionner plusieurs matières (Ctrl + Clic)
3. Cliquez sur "Créer la Classe"

**Important:** Sélectionnez toutes les matières que cette classe va étudier.

---

#### 1.5 Définir les Coefficients par Matière/Classe
**URL:** http://127.0.0.1:8000/admin/school_portal/subjectclass/

1. Cliquez sur "Ajouter matière-classe"
2. Remplissez :
   - **Subject:** Choisir une matière
   - **Classe:** Choisir une classe
   - **Coefficient:** Ex: 3 pour Maths, 2 pour Français, 1 pour EPS
3. Cliquez sur "Enregistrer"

**Exemple de coefficients pour une 3ème:**
- Mathématiques: Coefficient 3
- Français: Coefficient 3
- Anglais: Coefficient 2
- Sciences Physiques: Coefficient 2
- SVT: Coefficient 2
- Histoire-Géographie: Coefficient 2
- EPS: Coefficient 1

**Répéter pour chaque matière de chaque classe.**

---

### ÉTAPE 2 : Gestion des Étudiants

#### 2.1 Créer des Étudiants
**URL:** http://127.0.0.1:8000/portal/students/

1. Cliquez sur "Nouvel Étudiant"
2. Remplissez tous les champs
3. Cliquez sur "Enregistrer"

---

#### 2.2 Assigner des Étudiants à une Classe
**URL:** http://127.0.0.1:8000/admin/school_portal/class/

**Méthode 1 - Via l'Admin:**
1. Cliquez sur une classe
2. Dans le champ "Students", sélectionnez les étudiants (Ctrl + Clic pour sélection multiple)
3. Cliquez sur "Enregistrer"

**Méthode 2 - Via l'interface:**
1. Allez sur http://127.0.0.1:8000/portal/classes/
2. Cliquez sur une classe pour voir les détails
3. *(Interface d'assignation à implémenter si nécessaire)*

---

### ÉTAPE 3 : Saisie des Notes

#### 3.1 Ajouter une Note Individuelle
**URL:** http://127.0.0.1:8000/portal/grades/

1. Cliquez sur "Ajouter Note" (bouton bleu en haut à droite)
2. Remplissez le formulaire dans la modale :
   - **Étudiant:** Sélectionner un étudiant
   - **Matière:** Sélectionner une matière
   - **Type d'Évaluation:** Devoir, Composition, Interrogation, Examen, TP
   - **Note sur 20:** Saisir la note (Ex: 15.5)
   - **Coefficient:** Coefficient de cette évaluation (généralement 1)
   - **Date:** Date de l'évaluation
   - **Observations:** Commentaires (optionnel)
3. Cliquez sur "Enregistrer"

**Note:** La note est automatiquement liée à la période active.

---

#### 3.2 Saisie Rapide par Classe (Tableau)
**URL:** http://127.0.0.1:8000/portal/grades/

1. Sélectionnez une **Classe** dans le filtre
2. Sélectionnez une **Période** (optionnel)
3. Le tableau affiche tous les étudiants de la classe avec toutes les matières
4. Saisissez les notes directement dans les cellules
5. Les notes sont automatiquement sauvegardées

**Fonctionnalités du tableau:**
- Calcul automatique de la moyenne par étudiant
- Calcul automatique du rang dans la classe
- Affichage des coefficients
- Moyennes par matière

---

### ÉTAPE 4 : Consultation et Calculs

#### 4.1 Voir les Moyennes d'une Classe
**URL:** http://127.0.0.1:8000/portal/grades/

1. Sélectionnez une classe
2. Sélectionnez une période
3. Cliquez sur "Calculer Moyennes"

**Le système affiche:**
- Moyenne de chaque étudiant (avec coefficients)
- Rang de chaque étudiant
- Moyenne générale de la classe
- Meilleure note de la classe

---

#### 4.2 Générer un Bulletin de Notes
**URL:** http://127.0.0.1:8000/portal/students/{id}/

1. Allez sur la page de détails d'un étudiant
2. Cliquez sur "Bulletin de Notes"
3. Le bulletin s'affiche avec :
   - Notes par matière avec coefficients
   - Moyennes par matière
   - Moyenne générale
   - Rang dans la classe
   - Appréciations automatiques
   - Observations du conseil de classe

**Fonctions disponibles:**
- **Imprimer:** Utiliser le bouton d'impression du navigateur
- **Exporter PDF:** *(À implémenter)*
- **Envoyer par email:** *(À implémenter)*

---

#### 4.3 Liste de Tous les Bulletins
**URL:** http://127.0.0.1:8000/portal/reports/

1. Filtrer par classe et/ou période
2. Voir la liste de tous les étudiants
3. Actions disponibles par étudiant :
   - Voir le bulletin
   - Imprimer
   - Télécharger PDF

**Actions en masse:**
- Imprimer tous les bulletins d'une classe
- Générer PDF pour toute la classe
- Envoyer par email

---

## CALCULS AUTOMATIQUES

### Calcul de la Moyenne par Matière

```
Moyenne_Matière = Somme(Note × Coefficient_Evaluation) / Somme(Coefficients_Evaluations)
```

**Exemple:**
- Devoir 1 : 12/20 (coef 1)
- Devoir 2 : 15/20 (coef 1)
- Composition : 14/20 (coef 2)

Moyenne = (12×1 + 15×1 + 14×2) / (1+1+2) = 55/4 = **13.75/20**

---

### Calcul de la Moyenne Générale

```
Moyenne_Générale = Somme(Moyenne_Matière × Coefficient_Matière) / Somme(Coefficients_Matières)
```

**Exemple pour une 3ème:**
- Mathématiques : 14/20 (coef 3) → 42 points
- Français : 13/20 (coef 3) → 39 points
- Anglais : 15/20 (coef 2) → 30 points
- Sciences : 12/20 (coef 2) → 24 points
- Histoire-Géo : 11/20 (coef 2) → 22 points
- EPS : 16/20 (coef 1) → 16 points

**Total:** 173 points / 13 coefficients = **13.31/20**

---

### Calcul du Rang

Le rang est calculé en triant tous les étudiants de la classe par moyenne générale décroissante.

**Exemple:**
1. Jean KABORE : 15.50/20 → **Rang 1/30**
2. Marie OUEDRAOGO : 15.20/20 → **Rang 2/30**
3. Paul TRAORE : 14.80/20 → **Rang 3/30**
...

---

## APPRÉCIATIONS AUTOMATIQUES

Le système génère automatiquement des appréciations selon la moyenne :

| Moyenne | Appréciation |
|---------|-------------|
| >= 16 | Excellent élève. Travail remarquable... |
| >= 14 | Très bon élève. Résultats très satisfaisants... |
| >= 12 | Bon élève. Travail satisfaisant... |
| >= 10 | Élève moyen. Travail acceptable... |
| < 10 | Résultats insuffisants. Doit redoubler d'efforts... |

---

## FONCTIONNALITÉS AVANCÉES

### 1. Périodes Multiples
- Gérer plusieurs trimestres dans l'année
- Comparer les performances entre trimestres
- Calculer la moyenne annuelle

### 2. Types d'Évaluations
- **Devoir:** Évaluation régulière (coef 1)
- **Composition:** Examen important (coef 2-3)
- **Interrogation:** Test court (coef 1)
- **Examen:** Évaluation finale (coef 3-4)
- **TP:** Travaux pratiques (coef 1-2)

### 3. Export et Impression
- Bulletin PDF individuel
- Bulletin PDF par classe
- Export Excel des notes
- Import Excel des notes *(à implémenter)*

---

## WORKFLOW RECOMMANDÉ POUR UN TRIMESTRE

### Début de Trimestre
1. ✅ Créer la période du trimestre
2. ✅ Activer la période
3. ✅ Vérifier les classes et les étudiants
4. ✅ Vérifier les matières et coefficients

### Pendant le Trimestre
1. ✅ Saisir les notes au fur et à mesure
2. ✅ Utiliser différents types d'évaluation
3. ✅ Vérifier les moyennes régulièrement

### Fin de Trimestre
1. ✅ Vérifier que toutes les notes sont saisies
2. ✅ Calculer les moyennes finales
3. ✅ Générer les bulletins
4. ✅ Imprimer/distribuer les bulletins
5. ✅ Désactiver la période du trimestre
6. ✅ Créer la période suivante

---

## DÉPANNAGE

### Problème : Les moyennes ne s'affichent pas
**Solution:**
- Vérifier qu'il y a des notes saisies
- Vérifier que les coefficients sont définis (SubjectClass)
- Vérifier que la période est active

### Problème : Un étudiant n'apparaît pas dans la liste
**Solution:**
- Vérifier qu'il est assigné à une classe
- Rafraîchir la page

### Problème : Les coefficients ne sont pas pris en compte
**Solution:**
- Aller dans Admin > Matière-Classe
- Vérifier que chaque matière de chaque classe a un coefficient défini
- Par défaut, le coefficient est 1

---

## URLS PRINCIPALES

| Fonctionnalité | URL |
|---------------|-----|
| Dashboard | `/dashboard/` |
| Classes | `/portal/classes/` |
| Étudiants | `/portal/students/` |
| Enseignants | `/portal/teachers/` |
| Matières | `/portal/subjects/` |
| Gestion des Notes | `/portal/grades/` |
| Bulletins | `/portal/reports/` |
| Admin Django | `/admin/` |

---

## DONNÉES DE TEST (Optionnel)

Pour tester le système rapidement, créez :

**1 Classe:** 3ème A (Niveau: 3ème)

**6 Matières avec Coefficients:**
- Mathématiques (coef 3)
- Français (coef 3)
- Anglais (coef 2)
- Sciences (coef 2)
- Histoire (coef 2)
- EPS (coef 1)

**5 Étudiants:**
- Jean KABORE
- Marie OUEDRAOGO
- Paul TRAORE
- Fatima SAWADOGO
- Ibrahim ZONGO

**Saisir quelques notes** pour chaque étudiant dans chaque matière pour voir les calculs de moyennes et les bulletins.

---

## SUPPORT

Pour toute question ou problème :
1. Vérifier ce guide
2. Consulter les logs du serveur Django
3. Vérifier les données dans l'admin Django

**Bonne utilisation du système de gestion des notes ! 📚**
