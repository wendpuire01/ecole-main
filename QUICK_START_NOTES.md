# DÉMARRAGE RAPIDE - Système de Notes

## 🚀 Configuration en 5 Minutes

### 1. Créer une Période (Admin Django)
```
URL: http://127.0.0.1:8000/admin/school_portal/period/add/

- Name: 1er Trimestre
- Academic year: 2024-2025
- Start date: 2024-09-15
- End date: 2024-12-20
- ✓ Is active: COCHER
```

### 2. Créer un Enseignant
```
URL: http://127.0.0.1:8000/portal/teachers/create/

- Nom: OUEDRAOGO
- Prénom: Paul
- Deuxième Prénom: André
- Date de Naissance: 1985-05-10
- Email: p.ouedraogo@ecole.bf
- Téléphone: +226 70123456
- Adresse: Ouagadougou
```

### 3. Créer les Matières
```
URL: http://127.0.0.1:8000/portal/subjects/create/

Créer ces 6 matières:
- Mathématiques (Enseignant: OUEDRAOGO Paul)
- Français
- Anglais
- Sciences Physiques
- Histoire-Géographie
- EPS
```

### 4. Créer une Classe
```
URL: http://127.0.0.1:8000/portal/classes/

Cliquer "Nouvelle Classe":
- Nom: 3ème A
- Niveau: 3ème
- Enseignant Titulaire: OUEDRAOGO Paul
- Matières: TOUTES (Ctrl+Clic pour sélectionner les 6)
```

### 5. Définir les Coefficients
```
URL: http://127.0.0.1:8000/admin/school_portal/subjectclass/

Pour chaque matière de la classe 3ème A:
- Mathématiques + 3ème A → Coefficient: 3
- Français + 3ème A → Coefficient: 3
- Anglais + 3ème A → Coefficient: 2
- Sciences Physiques + 3ème A → Coefficient: 2
- Histoire-Géographie + 3ème A → Coefficient: 2
- EPS + 3ème A → Coefficient: 1
```

### 6. Créer des Étudiants
```
URL: http://127.0.0.1:8000/portal/students/

Créer 3-5 étudiants:
- Nom: KABORE, Prénom: Jean, Surname: Baptiste, etc.
- Nom: OUEDRAOGO, Prénom: Marie, Surname: Claire, etc.
- Nom: TRAORE, Prénom: Paul, Surname: François, etc.
```

### 7. Assigner Étudiants à la Classe
```
URL: http://127.0.0.1:8000/admin/school_portal/class/

- Cliquer sur "3ème A"
- Dans "Students": Sélectionner tous les étudiants créés (Ctrl+Clic)
- Cliquer "Enregistrer"
```

### 8. Saisir des Notes
```
URL: http://127.0.0.1:8000/portal/grades/

Cliquer "Ajouter Note":
- Étudiant: KABORE Jean Baptiste
- Matière: Mathématiques
- Type: Composition
- Note: 15.5
- Coefficient: 1
- Date: Aujourd'hui
→ Enregistrer

Répéter pour créer 2-3 notes par étudiant
```

### 9. Voir les Moyennes
```
URL: http://127.0.0.1:8000/portal/grades/

- Sélectionner Classe: 3ème A
- Sélectionner Période: 1er Trimestre
- Cliquer "Calculer Moyennes"

→ Vous verrez les moyennes de chaque étudiant !
```

### 10. Générer un Bulletin
```
URL: http://127.0.0.1:8000/portal/reports/

- Trouver un étudiant
- Cliquer "Bulletin"
→ Le bulletin s'affiche avec moyenne, rang, et appréciation
```

---

## ✅ CHECKLIST DE VÉRIFICATION

Avant de saisir des notes, vérifiez:

- [ ] Une période est créée et **ACTIVE**
- [ ] Les classes sont créées
- [ ] Les matières sont créées
- [ ] Les matières sont assignées aux classes
- [ ] Les **COEFFICIENTS** sont définis (SubjectClass)
- [ ] Les étudiants sont créés
- [ ] Les étudiants sont **ASSIGNÉS** aux classes

**⚠️ POINT CRITIQUE:** Les coefficients (étape 5) sont ESSENTIELS pour le calcul des moyennes !

---

## 📊 FORMULES DE CALCUL

**Moyenne d'une Matière:**
```
(Note1×Coef1 + Note2×Coef2 + ...) / (Coef1 + Coef2 + ...)
```

**Moyenne Générale:**
```
(MoyMath×3 + MoyFr×3 + MoyAng×2 + MoySci×2 + MoyHist×2 + MoyEPS×1) / 13
```

**Exemple:**
- Maths: 14/20 (coef 3) = 42 points
- Français: 13/20 (coef 3) = 39 points
- Anglais: 15/20 (coef 2) = 30 points
- Sciences: 12/20 (coef 2) = 24 points
- Histoire: 11/20 (coef 2) = 22 points
- EPS: 16/20 (coef 1) = 16 points

**Total:** 173 / 13 = **13.31/20**

---

## 🎯 URLS RAPIDES

| Page | URL |
|------|-----|
| Dashboard | http://127.0.0.1:8000/dashboard/ |
| Gestion Notes | http://127.0.0.1:8000/portal/grades/ |
| Bulletins | http://127.0.0.1:8000/portal/reports/ |
| Admin | http://127.0.0.1:8000/admin/ |

---

## 🐛 PROBLÈMES FRÉQUENTS

**Les moyennes sont à 0 ou n'apparaissent pas:**
→ Vérifier que les coefficients sont définis dans SubjectClass

**Un étudiant n'apparaît pas:**
→ Vérifier qu'il est assigné à une classe dans l'admin

**La classe ne s'affiche pas:**
→ Vérifier qu'elle a au moins une matière assignée

---

Pour un guide complet, voir: **GUIDE_GESTION_NOTES.md**
