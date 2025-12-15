# Guide de Design Moderne - Application de Gestion d'École

## Palette de Couleurs

### Couleurs Principales
```css
--primary: #4F46E5        /* Indigo moderne */
--primary-dark: #4338CA
--primary-light: #818CF8

--secondary: #06B6D4      /* Cyan professionnel */
--secondary-dark: #0891B2
--secondary-light: #22D3EE

--accent: #F59E0B         /* Amber pour les alertes */
--success: #10B981        /* Vert pour succès */
--danger: #EF4444         /* Rouge pour erreurs */
--warning: #F59E0B        /* Orange pour avertissements */
--info: #3B82F6           /* Bleu pour informations */
```

### Couleurs Neutres
```css
--gray-50: #F9FAFB
--gray-100: #F3F4F6
--gray-200: #E5E7EB
--gray-300: #D1D5DB
--gray-400: #9CA3AF
--gray-500: #6B7280
--gray-600: #4B5563
--gray-700: #374151
--gray-800: #1F2937
--gray-900: #111827
```

## Typographie

### Polices Recommandées
```css
/* Titres */
font-family: 'Inter', 'Segoe UI', sans-serif;

/* Corps de texte */
font-family: 'Inter', 'Roboto', 'Arial', sans-serif;

/* Chiffres/Données */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

### Hiérarchie
- **H1**: 2.5rem (40px) - Bold - Titres de pages principales
- **H2**: 2rem (32px) - Semibold - Sections
- **H3**: 1.5rem (24px) - Semibold - Sous-sections
- **H4**: 1.25rem (20px) - Medium - Cartes et widgets
- **Body**: 1rem (16px) - Regular - Texte principal
- **Small**: 0.875rem (14px) - Regular - Métadonnées

## Composants UI Modernes

### 1. Cards (Cartes)
```html
<div class="card shadow-lg rounded-xl border-0 overflow-hidden">
  <div class="card-header bg-gradient-primary text-white p-4">
    <h3 class="mb-0">Titre de la carte</h3>
  </div>
  <div class="card-body p-4">
    Contenu
  </div>
</div>
```

### 2. Boutons avec États
```html
<!-- Primary -->
<button class="btn btn-primary shadow-sm hover:shadow-lg transition-all">
  Action Principale
</button>

<!-- Secondary -->
<button class="btn btn-outline-primary hover:bg-primary transition-all">
  Action Secondaire
</button>

<!-- Icon Button -->
<button class="btn btn-icon rounded-full w-10 h-10">
  <i class="fas fa-plus"></i>
</button>
```

### 3. Formulaires Élégants
```html
<div class="form-group mb-4">
  <label class="form-label text-gray-700 font-medium mb-2">
    Nom de l'étudiant
  </label>
  <input type="text"
         class="form-control rounded-lg border-gray-300
                focus:border-primary focus:ring-2
                focus:ring-primary/20 transition-all"
         placeholder="Entrez le nom">
  <small class="form-text text-gray-500 mt-1">
    Information supplémentaire
  </small>
</div>
```

### 4. Tables Modernes
```html
<div class="table-responsive rounded-lg shadow-sm overflow-hidden">
  <table class="table table-hover">
    <thead class="bg-gray-50 border-b-2 border-gray-200">
      <tr>
        <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
          Colonne
        </th>
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
      <tr class="hover:bg-gray-50 transition-colors">
        <td class="px-6 py-4 text-sm text-gray-900">
          Données
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### 5. Badges et Statuts
```html
<!-- Statut Payé -->
<span class="badge bg-success rounded-full px-3 py-1 text-xs font-medium">
  Payé
</span>

<!-- Statut En attente -->
<span class="badge bg-warning rounded-full px-3 py-1 text-xs font-medium">
  En attente
</span>

<!-- Statut Impayé -->
<span class="badge bg-danger rounded-full px-3 py-1 text-xs font-medium">
  Impayé
</span>
```

## Layout Structure

### Dashboard Principal
```
┌─────────────────────────────────────────────────────┐
│ SIDEBAR          │  HEADER (Recherche, Notifications)│
│                  ├─────────────────────────────────────┤
│ Navigation       │                                    │
│ - Dashboard      │  ZONE DE CONTENU PRINCIPALE       │
│ - Étudiants      │                                    │
│ - Finance        │  Cards avec statistiques          │
│ - Classes        │  Graphiques                       │
│ - Notes          │  Tables de données                │
│ - Bulletins      │                                    │
│                  │                                    │
└─────────────────────────────────────────────────────┘
```

### Responsive Breakpoints
```css
/* Mobile */
@media (max-width: 768px) {
  /* Sidebar devient bottom nav */
  /* Cards en pleine largeur */
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1024px) {
  /* Sidebar collapsible */
  /* 2 colonnes pour cards */
}

/* Desktop */
@media (min-width: 1024px) {
  /* Sidebar fixe */
  /* 3-4 colonnes pour cards */
}
```

## Icônes Modernes (FontAwesome 6)

### Finance
- `fa-solid fa-money-bill-wave` - Paiements
- `fa-solid fa-wallet` - Portefeuille
- `fa-solid fa-receipt` - Reçus
- `fa-solid fa-credit-card` - Carte de crédit
- `fa-solid fa-chart-line` - Statistiques

### Académique
- `fa-solid fa-graduation-cap` - Étudiants
- `fa-solid fa-chalkboard-user` - Classes
- `fa-solid fa-book-open` - Matières
- `fa-solid fa-clipboard-list` - Notes
- `fa-solid fa-trophy` - Réussites

### Actions
- `fa-solid fa-plus` - Ajouter
- `fa-solid fa-edit` - Modifier
- `fa-solid fa-trash` - Supprimer
- `fa-solid fa-eye` - Voir
- `fa-solid fa-print` - Imprimer
- `fa-solid fa-download` - Télécharger

## Animations et Transitions

### Hover Effects
```css
.card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
```

### Loading States
```css
.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## Exemples de Composants Métier

### Card Statistique
```html
<div class="stat-card bg-white rounded-xl shadow-sm p-6 border-l-4 border-primary">
  <div class="flex items-center justify-between">
    <div>
      <p class="text-sm text-gray-600 font-medium">Total Étudiants</p>
      <h3 class="text-3xl font-bold text-gray-900 mt-2">1,234</h3>
      <p class="text-sm text-green-600 mt-1">
        <i class="fas fa-arrow-up"></i> +12% ce mois
      </p>
    </div>
    <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
      <i class="fas fa-users text-primary text-2xl"></i>
    </div>
  </div>
</div>
```

### Liste Paiements
```html
<div class="payment-item flex items-center justify-between p-4 border-b hover:bg-gray-50">
  <div class="flex items-center space-x-4">
    <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
      <i class="fas fa-check text-green-600"></i>
    </div>
    <div>
      <h4 class="font-semibold text-gray-900">Jean Kabore</h4>
      <p class="text-sm text-gray-500">Scolarité - Trimestre 1</p>
    </div>
  </div>
  <div class="text-right">
    <p class="font-bold text-gray-900">150,000 FCFA</p>
    <p class="text-sm text-gray-500">15 Dec 2025</p>
  </div>
</div>
```

### Bulletin de Notes (Preview)
```html
<div class="report-card bg-white rounded-lg shadow-lg p-8 max-w-4xl mx-auto">
  <!-- En-tête -->
  <div class="header text-center border-b-2 border-primary pb-6 mb-6">
    <h1 class="text-3xl font-bold text-gray-900">BULLETIN SCOLAIRE</h1>
    <p class="text-gray-600 mt-2">Année Académique 2024-2025</p>
  </div>

  <!-- Infos Étudiant -->
  <div class="student-info grid grid-cols-2 gap-4 mb-6 bg-gray-50 p-4 rounded-lg">
    <div>
      <span class="text-sm text-gray-600">Nom:</span>
      <span class="font-semibold ml-2">KABORE Jean</span>
    </div>
    <div>
      <span class="text-sm text-gray-600">Classe:</span>
      <span class="font-semibold ml-2">Terminale S1</span>
    </div>
  </div>

  <!-- Notes -->
  <table class="w-full mb-6">
    <thead class="bg-primary text-white">
      <tr>
        <th class="p-3 text-left">Matière</th>
        <th class="p-3 text-center">Note</th>
        <th class="p-3 text-center">Coef</th>
        <th class="p-3 text-center">Total</th>
      </tr>
    </thead>
    <tbody class="divide-y">
      <tr>
        <td class="p-3">Mathématiques</td>
        <td class="p-3 text-center font-semibold">15.5</td>
        <td class="p-3 text-center">4</td>
        <td class="p-3 text-center font-bold">62</td>
      </tr>
    </tbody>
  </table>

  <!-- Moyenne Générale -->
  <div class="bg-primary text-white p-4 rounded-lg text-center">
    <p class="text-sm font-medium">Moyenne Générale</p>
    <p class="text-4xl font-bold mt-2">14.75/20</p>
  </div>
</div>
```

## Dark Mode (Optionnel)

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1F2937;
    --bg-secondary: #111827;
    --text-primary: #F9FAFB;
    --text-secondary: #D1D5DB;
    --border: #374151;
  }
}
```

## Principes de Design

1. **Espace Blanc**: Utilisez généreusement l'espace pour la respiration
2. **Hiérarchie Visuelle**: Tailles, poids et couleurs pour guider l'œil
3. **Consistance**: Mêmes composants, mêmes comportements
4. **Feedback Utilisateur**: États hover, focus, active, disabled
5. **Accessibilité**: Contraste suffisant, labels clairs, navigation au clavier
6. **Performance**: Images optimisées, animations fluides (60fps)
7. **Mobile First**: Design d'abord pour mobile, puis desktop

## Outils & Frameworks

- **CSS Framework**: Bootstrap 5 ou Tailwind CSS
- **Icons**: FontAwesome 6 Pro
- **Charts**: Chart.js ou ApexCharts
- **Animations**: Animate.css ou custom CSS
- **Datepickers**: Flatpickr
- **Select**: Choices.js ou Select2
