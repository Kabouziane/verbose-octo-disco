# Frontend Vue.js - E-commerce & Comptabilité

## Installation

```bash
cd frontend
npm install
```

## Développement

```bash
npm run dev
```

L'application sera disponible sur `http://localhost:3000`

## Fonctionnalités

### 🔐 **Authentification**
- Connexion JWT
- Protection des routes
- Gestion automatique des tokens

### 📊 **Dashboard**
- Statistiques en temps réel
- Graphiques des ventes
- Répartition TVA
- Dernières activités

### 📦 **Gestion Produits**
- Liste avec filtres et recherche
- Création/modification de produits
- Gestion des stocks
- Images produits

### 🧾 **Facturation**
- Création de factures
- Suivi des paiements
- Export PDF

### 📚 **Comptabilité**
- Plan comptable belge
- Écritures comptables
- Balance de vérification

### 💰 **TVA**
- Déclarations automatiques
- Grilles belges
- Calculs par période

## Structure

```
src/
├── components/     # Composants réutilisables
├── views/         # Pages principales
├── services/      # API calls
├── store/         # Vuex store
└── router/        # Configuration routes
```

## Technologies

- **Vue 3** - Framework JavaScript
- **Vue Router** - Routage
- **Vuex** - Gestion d'état
- **Axios** - Requêtes HTTP
- **Bootstrap 5** - UI Framework
- **Chart.js** - Graphiques
- **Font Awesome** - Icônes