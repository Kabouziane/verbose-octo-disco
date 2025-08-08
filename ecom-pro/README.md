# 🚀 API E-commerce Django avec Comptabilité Belge - SYSTÈME COMPLET

## 🎯 Vue d'ensemble

Système e-commerce complet avec comptabilité belge, optimisations avancées (cache, cookies, performance) et interface Vue.js moderne.

## 🏗️ Architecture du Projet

Cette API Django REST Framework est structurée en trois applications principales avec optimisations avancées :

### 1. **Shop** - Gestion E-commerce 🛒
- **Produits et catégories** : CRUD complet avec gestion des images et cache intelligent
- **Gestion des stocks** : Suivi automatique, alertes de stock minimum
- **Paniers et wishlist** : Gestion des paniers utilisateurs et listes de souhaits (avec cookies pour invités)
- **Commandes** : Workflow complet de commande avec statuts
- **Paiements** : Intégration Stripe pour les paiements en ligne
- **Clients** : Profils clients B2B/B2C avec validation TVA automatique
- **Validation TVA** : Validation européenne via VIES SOAP API

### 2. **Service** - Services et Support 🏢
- **Services** : Abonnements, prestations ponctuelles, consultations (avec cache)
- **Rendez-vous** : Système de réservation avec créneaux disponibles
- **Support technique** : Système de tickets avec messages en temps réel
- **Abonnements** : Gestion des abonnements récurrents avec renouvellement automatique
- **Avis clients** : Système d'évaluation des services avec prévention des doublons

### 3. **Admin Dashboard** - Administration Interne 📊
- **Ressources Humaines** : Employés, départements, congés avec workflow d'approbation
- **Comptabilité Belge** : Conforme au PCMN (Plan Comptable Minimum Normalisé)
- **Facturation** : Génération et suivi des factures avec calculs automatiques optimisés
- **Déclarations TVA** : Génération automatique des déclarations TVA belges
- **Paiements** : Suivi des paiements et soldes clients
- **Écritures comptables** : Gestion complète avec balance de vérification

### 4. **Optimisations Avancées** ⚡
- **Système de cache** : Cache intelligent avec invalidation automatique
- **Gestion des cookies** : Cookies sécurisés avec préférences utilisateur
- **Optimisations low-level** : Traitement asynchrone, monitoring mémoire
- **Middleware personnalisés** : Performance, sécurité, rate limiting
- **Interface Vue.js** : Frontend moderne et réactif

## Spécificités Comptables Belges

### Plan Comptable (PCMN)
Le système implémente le Plan Comptable Minimum Normalisé belge avec :
- **Classe 1** : Fonds propres, provisions et dettes à plus d'un an
- **Classe 2** : Frais d'établissement, actifs immobilisés
- **Classe 3** : Stock et commandes en cours d'exécution
- **Classe 4** : Créances et dettes à un an au plus
- **Classe 5** : Placements de trésorerie et valeurs disponibles
- **Classe 6** : Charges
- **Classe 7** : Produits

### Journaux Comptables
- **VTE** : Journal des ventes
- **ACH** : Journal des achats
- **CAI** : Journal de caisse
- **BNQ** : Journal de banque
- **OD** : Opérations diverses

### TVA Belge
Gestion des taux de TVA belges :
- **21%** : Taux normal
- **6%** : Taux réduit
- **0%** : Taux zéro

### Déclarations TVA
Génération automatique des déclarations avec les grilles officielles :
- Grilles 00-03 : Opérations par taux de TVA
- Grilles 54-56 : TVA due
- Grille 59 : TVA déductible
- Grilles 71-72 : Solde à payer/récupérer

## Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd drf-ecom
```

2. **Créer l'environnement virtuel**
```bash
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration des variables d'environnement**
```bash
# Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres (optionnel pour SQLite)
```

5. **Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Initialiser le plan comptable belge**
```bash
python manage.py setup_belgian_accounting
```

7. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

8. **Optimisations système (optionnel)**
```bash
python startup_optimizations.py
```

9. **Tests complets**
```bash
python run_tests.py
```

10. **Lancer le serveur**
```bash
python manage.py runserver
```

11. **Frontend (terminal séparé)**
```bash
cd frontend
npm install
npm run dev
```

## 🔗 Endpoints API Principaux

### Authentification
- `POST /api/auth/token/` - Obtenir un token JWT
- `POST /api/auth/token/refresh/` - Rafraîchir le token

### Shop
- `GET /api/shop/products/` - Liste des produits (avec cache)
- `POST /api/shop/customers/` - Créer un client
- `POST /api/shop/customers/validate_vat/` - Valider numéro TVA
- `POST /api/shop/cart/{id}/add_item/` - Ajouter au panier
- `POST /api/shop/orders/` - Créer une commande
- `POST /api/shop/orders/{id}/create_payment_intent/` - Paiement Stripe

### Service
- `GET /api/service/services/` - Liste des services
- `POST /api/service/appointments/` - Réserver un rendez-vous
- `POST /api/service/tickets/` - Créer un ticket de support

### Admin Dashboard
- `GET /api/admin-dashboard/employees/` - Gestion des employés
- `POST /api/admin-dashboard/invoices/` - Créer une facture (optimisée)
- `GET /api/admin-dashboard/invoices/{id}/download_pdf/` - Télécharger PDF
- `POST /api/admin-dashboard/invoices/{id}/send_email/` - Envoyer par email
- `POST /api/admin-dashboard/vat-declarations/generate_declaration/` - Générer déclaration TVA
- `GET /api/admin-dashboard/accounting-entries/trial_balance/` - Balance de vérification

## 📚 Documentation et Interfaces

### API Documentation
- **Swagger UI** : `http://localhost:8000/api/docs/`
- **Schema OpenAPI** : `http://localhost:8000/api/schema/`

### Interfaces Utilisateur
- **Frontend Vue.js** : `http://localhost:3000`
- **Admin Django** : `http://localhost:8000/admin/`

### Monitoring
- **Headers de performance** : X-Response-Time, X-DB-Queries
- **Logs séparés** : django.log, cache.log, performance.log

## 🛠️ Technologies Utilisées

### Backend
- **Django 5.0** : Framework web Python
- **Django REST Framework** : API REST avec optimisations
- **SQLite/PostgreSQL** : Base de données avec optimisations
- **JWT** : Authentification sécurisée
- **Stripe** : Paiements en ligne
- **Redis** : Cache et sessions (optionnel)
- **drf-spectacular** : Documentation API interactive

### Frontend
- **Vue.js 3** : Framework JavaScript moderne
- **Vue Router** : Navigation SPA
- **Axios** : Client HTTP
- **Bootstrap 5** : Framework CSS

### Optimisations
- **Cache système** : LocMemCache/Redis avec gestionnaire avancé
- **Cookies sécurisés** : HttpOnly, Secure, SameSite
- **Traitement asynchrone** : ThreadPoolExecutor
- **Monitoring** : Performance et mémoire en temps réel
- **Middleware** : Sécurité, rate limiting, compression

## Conformité Légale Belge

Le système respecte la législation comptable belge :
- **Arrêté royal du 29 avril 2019** relatif au plan comptable minimum normalisé
- **Code de la TVA** belge pour les taux et déclarations
- **Loi comptable** du 17 juillet 1975 pour la tenue des livres comptables

## 🛡️ Sécurité et Performance

### Sécurité
- **Authentification JWT** obligatoire pour les endpoints sensibles
- **Permissions granulaires** par rôle utilisateur
- **Headers de sécurité** : CSP, XSS Protection, X-Frame-Options
- **Rate limiting** : 100 requêtes/minute par IP
- **Cookies sécurisés** : HttpOnly, Secure, SameSite
- **Validation des données** d'entrée avec sanitisation
- **Protection CORS** configurée
- **Variables d'environnement** pour les secrets

### Performance
- **Cache intelligent** avec invalidation automatique
- **Optimisations mémoire** avec garbage collection
- **Traitement asynchrone** pour les tâches lourdes
- **Bulk operations** pour les opérations de masse
- **Monitoring en temps réel** des performances
- **Compression** des réponses HTTP
- **Pool de connexions** optimisé

## 🧪 Tests

### Suite de tests complète
```bash
python run_tests.py
```

### Tests par application
```bash
python manage.py test shop.tests
python manage.py test service.tests
python manage.py test admin_dashboard.tests
```

### Couverture
- **Shop** : Clients, produits, commandes, paniers, validation TVA
- **Service** : Services, rendez-vous, support, abonnements, avis
- **Admin** : Employés, comptabilité, factures, déclarations TVA

## 📁 Structure Avancée

```
drf-ecom/
├── shop/                          # E-commerce
├── service/                       # Services
├── admin_dashboard/               # Administration
├── frontend/                      # Interface Vue.js
├── cache_system.py               # Cache avancé
├── cookie_manager.py             # Cookies sécurisés
├── low_level_optimizations.py   # Optimisations
├── middleware.py                 # Middleware personnalisés
├── startup_optimizations.py     # Script d'optimisation
├── run_tests.py                 # Suite de tests
├── requirements-advanced.txt    # Dépendances avancées
└── FINAL_SUMMARY.md             # Documentation complète
```

## 🚀 Fonctionnalités Avancées

### Cache Système
- **Gestionnaire centralisé** avec timeouts par catégorie
- **Décorateurs** : @cache_products, @cache_customers
- **Cache de session** utilisateur
- **Préchauffage automatique** au démarrage

### Cookies Sécurisés
- **Préférences utilisateur** : langue, thème, devise
- **Panier invité** pour utilisateurs non connectés
- **Sessions optimisées** avec cache
- **Sécurité avancée** : HttpOnly, Secure, SameSite

### Optimisations Low-Level
- **Traitement asynchrone** avec ThreadPoolExecutor
- **Monitoring mémoire** avec psutil
- **Bulk operations** pour les opérations de masse
- **Requêtes SQL brutes** optimisées
- **Garbage collection** automatique

### Middleware Avancés
- **Performance** : Monitoring temps de réponse
- **Cache** : Cache automatique des réponses API
- **Sécurité** : Headers CSP, XSS, rate limiting
- **Compression** : Optimisation des réponses
- **Database** : Monitoring des requêtes

## 🎯 Prêt pour la Production

✅ **Fonctionnalités complètes** : E-commerce + Comptabilité belge  
✅ **Optimisations avancées** : Cache + Performance + Sécurité  
✅ **Tests complets** : Couverture de toutes les fonctionnalités  
✅ **Interface moderne** : Vue.js responsive  
✅ **Documentation complète** : API + Code + Déploiement  
✅ **Conformité légale** : PCMN + TVA belge  

**Le système est entièrement opérationnel et optimisé !**