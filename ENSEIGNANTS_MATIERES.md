# Gestion des Enseignants par Matière et Classe

## 🎯 Système Flexible

Le système permet maintenant d'assigner **différents enseignants** pour la même matière dans différentes classes.

## 📋 Comment ça fonctionne

### Exemple Concret :

**Mathématiques** peut être enseignée par :
- M. OUEDRAOGO dans la classe **6ème A**
- Mme TRAORE dans la classe **6ème B**
- M. SAWADOGO dans la classe **Terminale S1**

Tous enseignent **Mathématiques**, mais **pas dans les mêmes classes**.

## 🔧 Structure des Données

### 1. **Subject (Matière)**
- `name` : Nom de la matière (ex: Mathématiques)
- `teacher` : Enseignant par défaut (optionnel, utilisé si aucun enseignant spécifique n'est assigné)
- `classes` : Liste des classes où cette matière est enseignée

### 2. **SubjectClass (Matière-Classe)** ⭐ NOUVEAU
Cette table fait le lien entre une matière et une classe, et permet de définir :
- `subject` : La matière
- `classe` : La classe
- `teacher` : **L'enseignant spécifique pour cette combinaison** (NOUVEAU !)
- `coefficient` : Le coefficient de la matière pour cette classe

## 💡 Utilisation via Admin Django

### Assigner un enseignant à une matière pour une classe :

1. Aller dans l'admin Django : `/admin/`
2. Cliquer sur **Matières-Classes** (SubjectClass)
3. Cliquer sur **Ajouter Matière-Classe**
4. Remplir :
   - **Subject** : Choisir la matière (ex: Mathématiques)
   - **Classe** : Choisir la classe (ex: 6ème A)
   - **Teacher** : Choisir l'enseignant (ex: M. OUEDRAOGO)
   - **Coefficient** : Entrer le coefficient (ex: 3)
5. Sauvegarder

### Répéter pour chaque classe :

Pour **Mathématiques** :
- 6ème A → M. OUEDRAOGO (coef: 2)
- 6ème B → Mme TRAORE (coef: 2)
- Terminale S1 → M. SAWADOGO (coef: 4)

## 📊 Priorité des Enseignants

Le système utilise cette logique :

1. **Priorité 1** : Enseignant défini dans `SubjectClass` (spécifique à la classe)
2. **Priorité 2** : Enseignant par défaut défini dans `Subject`

```python
# Récupérer l'enseignant de Maths pour la 6ème A
math_subject = Subject.objects.get(name="Mathématiques")
classe_6a = Class.objects.get(name="6ème A")

# Cette méthode retourne l'enseignant spécifique ou le défaut
teacher = math_subject.get_teacher_for_class(classe_6a)
```

## 🎓 Exemples Concrets

### Exemple 1 : Mathématiques

| Classe | Enseignant | Coefficient |
|--------|-----------|-------------|
| 6ème A | M. OUEDRAOGO | 2 |
| 6ème B | Mme TRAORE | 2 |
| Terminale S1 | M. SAWADOGO | 4 |
| Terminale S2 | M. SAWADOGO | 4 |

### Exemple 2 : Français

| Classe | Enseignant | Coefficient |
|--------|-----------|-------------|
| 6ème A | Mme KABORE | 3 |
| 6ème B | Mme KABORE | 3 |
| Terminale S1 | M. ZONGO | 2 |

### Exemple 3 : SVT

| Classe | Enseignant | Coefficient |
|--------|-----------|-------------|
| 6ème A | M. COMPAORE | 2 |
| Terminale S1 | Mme OUEDRAOGO | 3 |
| Terminale S2 | Mme OUEDRAOGO | 3 |

## ✅ Avantages du Système

1. **Flexibilité** : Chaque enseignant peut avoir ses classes
2. **Coefficients différents** : Une matière peut avoir un coefficient différent selon la classe
3. **Bulletins précis** : Le nom du bon enseignant apparaît sur chaque bulletin
4. **Charge de travail** : Facile de voir quelles classes chaque enseignant a
5. **Remplacement facile** : Changer l'enseignant d'une classe sans affecter les autres

## 🔍 Requêtes Utiles

### Voir toutes les classes d'un enseignant :
```python
teacher = Teacher.objects.get(name="OUEDRAOGO")
subject_classes = SubjectClass.objects.filter(teacher=teacher)

for sc in subject_classes:
    print(f"{sc.subject.name} dans {sc.classe.name}")
```

### Voir tous les enseignants d'une classe :
```python
classe = Class.objects.get(name="6ème A")
subject_classes = SubjectClass.objects.filter(classe=classe)

for sc in subject_classes:
    teacher_name = sc.teacher.name if sc.teacher else "Non assigné"
    print(f"{sc.subject.name}: {teacher_name}")
```

## 🚀 Migration Appliquée

La migration a ajouté le champ `teacher` à la table `SubjectClass` :

```
✅ school_portal.0007_subjectclass_teacher - Applied
```

## 📝 Note Importante

- L'enseignant dans `Subject` reste **optionnel** et sert de **valeur par défaut**
- Pour préciser un enseignant par classe, utilisez `SubjectClass`
- Si aucun enseignant n'est défini dans `SubjectClass`, le système utilise l'enseignant par défaut du `Subject`

## 🎯 Prochaines Étapes Recommandées

1. Créer toutes les matières dans l'admin
2. Pour chaque matière, créer les entrées `SubjectClass` avec :
   - La classe
   - L'enseignant spécifique
   - Le coefficient approprié
3. Les bulletins afficheront automatiquement le bon enseignant pour chaque matière
