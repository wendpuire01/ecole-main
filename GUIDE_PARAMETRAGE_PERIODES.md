# 📚 Guide de Paramétrage des Périodes Scolaires

Ce guide vous explique **étape par étape** comment paramétrer le système de gestion des périodes pour générer correctement les bulletins.

---

## 🎯 Objectif

Configurer les **périodes scolaires** (trimestres ou semestres) pour que :
- ✅ Les bulletins affichent uniquement les notes de la période active
- ✅ Les moyennes des trimestres précédents apparaissent automatiquement
- ✅ L'année scolaire et le nom de la période soient dynamiques

---

## 🚀 Méthode 1 : Paramétrage Automatique (RECOMMANDÉ)

### Option A : Avec Activation Automatique

Créez toutes les périodes de l'année et activez automatiquement la première :

```bash
python manage.py setup_periods 2025-2026 --activate-first
```

**Résultat :**
```
Création des trimestres pour 2025-2026
----------------------------------------------------------------------
  ✓ 1er Trimestre        01/09/2025 - 15/12/2025 ✓ ACTIVE
  ✓ 2e Trimestre         05/01/2026 - 30/03/2026
  ✓ 3e Trimestre         01/04/2026 - 30/06/2026

======================================================================
✓ Paramétrage terminé avec succès!
======================================================================

Prochaines étapes:
  1. Vérifiez les périodes: python manage.py set_active_period --list
  2. Ou accédez à: http://localhost:8000/periods/
  3. Associez vos devoirs aux périodes lors de leur création
```

### Option B : Créer des Semestres au lieu de Trimestres

```bash
python manage.py setup_periods 2025-2026 --type semestre --activate-first
```

**Résultat :**
```
Création des semestres pour 2025-2026
----------------------------------------------------------------------
  ✓ 1er Semestre         01/09/2025 - 31/01/2026 ✓ ACTIVE
  ✓ 2e Semestre          01/02/2026 - 30/06/2026
```

### Option C : Recréer les Périodes (Supprimer et Recréer)

Si vous avez fait une erreur et voulez recommencer :

```bash
python manage.py setup_periods 2025-2026 --force --activate-first
```

---

## 🖥️ Méthode 2 : Paramétrage via Interface Web

### Étape 1 : Démarrer le serveur

```bash
python manage.py runserver
```

### Étape 2 : Accéder à la gestion des périodes

Ouvrez votre navigateur et allez sur :
```
http://localhost:8000/periods/
```

**Ou via le menu de navigation :**
```
Menu latéral → Administration → Périodes
```

### Étape 3 : Créer une nouvelle période

1. Cliquez sur le bouton **[➕ Créer une Période]**
2. Remplissez le formulaire :
   - **Année Scolaire** : `2025-2026`
   - **Période** : Sélectionnez `1er Trimestre`
   - **Date de Début** : `01/09/2025`
   - **Date de Fin** : `15/12/2025`
   - **Activer cette période** : ☑️ Coché (si c'est la période actuelle)
3. Cliquez sur **[Créer]**

### Étape 4 : Répéter pour toutes les périodes

Créez les autres périodes de la même manière :

| Période | Début | Fin |
|---------|-------|-----|
| 1er Trimestre | 01/09/2025 | 15/12/2025 |
| 2e Trimestre | 05/01/2026 | 30/03/2026 |
| 3e Trimestre | 01/04/2026 | 30/06/2026 |

---

## 🔄 Changer de Période Active

### Via l'interface web :

1. Allez sur `http://localhost:8000/periods/`
2. Trouvez la période que vous voulez activer
3. Cliquez sur le bouton **🔌** (bouton vert "Activer")
4. ✅ La période est maintenant active !

### Via la ligne de commande :

#### Lister les périodes disponibles :
```bash
python manage.py set_active_period --list
```

#### Activer une période par son ID :
```bash
python manage.py set_active_period 2
```

#### Activer une période par son nom :
```bash
python manage.py set_active_period --year 2025-2026 --period trimestre2
```

---

## 📝 Associer les Devoirs aux Périodes

**IMPORTANT :** Lors de la création d'un devoir ou d'une composition, vous devez **obligatoirement** l'associer à une période.

### Via l'interface d'administration Django :

1. Allez sur `http://localhost:8000/admin/`
2. Créez un nouveau **Assignment** (Devoir)
3. Dans le champ **Period**, sélectionnez la période active
4. Sauvegardez

### Via le code Python :

```python
from school_portal.models import Assignment, Period, Subject

# Récupérer la période active
current_period = Period.objects.get(is_active=True)

# Créer un devoir
assignment = Assignment.objects.create(
    title="Devoir de Mathématiques",
    subject=Subject.objects.get(name="Mathématiques"),
    evaluation_type='devoir',
    period=current_period,  # ✅ IMPORTANT
    max_points=20,
    due_date='2026-01-15'
)
```

---

## ✅ Vérification du Paramétrage

### 1. Vérifier les périodes créées :

```bash
python manage.py set_active_period --list
```

**Sortie attendue :**
```
Périodes disponibles:
================================================================================

Année Scolaire: 2025-2026
--------------------------------------------------------------------------------
  ID: 1    | 1er Trimestre        | 01/09/2025 - 15/12/2025 | ✓ ACTIVE
  ID: 2    | 2e Trimestre         | 05/01/2026 - 30/03/2026 |
  ID: 3    | 3e Trimestre         | 01/04/2026 - 30/06/2026 |
```

### 2. Vérifier qu'une période est active :

```bash
python manage.py shell
```

```python
>>> from school_portal.models import Period
>>> active_period = Period.objects.get(is_active=True)
>>> print(f"Période active: {active_period.get_name_display()} - {active_period.academic_year}")
```

**Sortie attendue :**
```
Période active: 1er Trimestre - 2025-2026
```

### 3. Tester la génération d'un bulletin :

1. Allez sur `http://localhost:8000/reports/`
2. Générez un bulletin pour un élève
3. Vérifiez que :
   - ✅ L'année scolaire affichée est `2025-2026`
   - ✅ La période affichée est `1er Trimestre`
   - ✅ Les notes affichées sont uniquement celles du 1er trimestre

---

## 🗓️ Calendrier Type (Système Trimestriel)

### Année Scolaire 2025-2026

| Période | Dates | À Activer |
|---------|-------|-----------|
| **1er Trimestre** | 01/09/2025 - 15/12/2025 | Septembre 2025 |
| **2e Trimestre** | 05/01/2026 - 30/03/2026 | Janvier 2026 |
| **3e Trimestre** | 01/04/2026 - 30/06/2026 | Avril 2026 |

---

## 🗓️ Calendrier Type (Système Semestriel)

### Année Scolaire 2025-2026

| Période | Dates | À Activer |
|---------|-------|-----------|
| **1er Semestre** | 01/09/2025 - 31/01/2026 | Septembre 2025 |
| **2e Semestre** | 01/02/2026 - 30/06/2026 | Février 2026 |

---

## 🔧 Commandes Utiles

### Créer les périodes pour une nouvelle année

```bash
# Trimestres
python manage.py setup_periods 2026-2027 --activate-first

# Semestres
python manage.py setup_periods 2026-2027 --type semestre --activate-first
```

### Lister toutes les périodes

```bash
python manage.py set_active_period --list
```

### Changer la période active

```bash
# Par ID
python manage.py set_active_period 3

# Par nom
python manage.py set_active_period --year 2025-2026 --period trimestre3
```

### Accéder à l'interface web de gestion

```
http://localhost:8000/periods/
```

---

## ⚠️ Points Importants

### ✅ À FAIRE :
- ✅ Créer les périodes au début de chaque année scolaire
- ✅ Activer UNE SEULE période à la fois
- ✅ Associer tous les devoirs à une période lors de leur création
- ✅ Changer la période active quand vous passez au trimestre suivant

### ❌ À NE PAS FAIRE :
- ❌ Avoir plusieurs périodes actives en même temps
- ❌ Créer des devoirs sans les associer à une période
- ❌ Supprimer une période qui contient déjà des notes
- ❌ Oublier de changer la période active au début d'un nouveau trimestre

---

## 🆘 Résolution de Problèmes

### Problème : Les bulletins montrent toutes les notes de tous les trimestres

**Cause :** Les devoirs ne sont pas associés à une période.

**Solution :**
1. Vérifiez que vous avez créé au moins une période
2. Vérifiez qu'une période est active
3. Associez tous vos devoirs existants à la bonne période

```python
python manage.py shell

>>> from school_portal.models import Assignment, Period
>>>
>>> # Récupérer la période du 1er trimestre
>>> period1 = Period.objects.get(name='trimestre1', academic_year='2025-2026')
>>>
>>> # Associer tous les devoirs créés en septembre-décembre à cette période
>>> Assignment.objects.filter(
...     due_date__gte='2025-09-01',
...     due_date__lte='2025-12-15'
... ).update(period=period1)
```

### Problème : Le message "Aucune période trouvée"

**Cause :** Vous n'avez pas encore créé de périodes.

**Solution :**
```bash
python manage.py setup_periods 2025-2026 --activate-first
```

### Problème : L'année affichée est "N/A"

**Cause :** Aucune période n'est active.

**Solution :**
```bash
# Lister les périodes
python manage.py set_active_period --list

# Activer une période
python manage.py set_active_period 1
```

---

## 📞 Support

Pour toute question ou problème :
1. Vérifiez ce guide
2. Consultez les logs Django
3. Vérifiez la console pour les erreurs JavaScript/CSS

---

## 🎉 Félicitations !

Votre système de gestion des périodes est maintenant configuré. Les bulletins afficheront automatiquement :
- ✅ Les notes du trimestre actif uniquement
- ✅ L'année scolaire dynamique
- ✅ Le nom de la période dynamique
- ✅ Les moyennes des trimestres précédents (à partir du 2e trimestre)

**Bon travail !** 🎓
