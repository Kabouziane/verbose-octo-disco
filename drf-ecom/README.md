# API E-commerce Django avec Comptabilité Belge

## Architecture du Projet

Cette API Django REST Framework est structurée en trois applications principales :

### 1. **Shop** - Gestion E-commerce
- **Produits et catégories** : CRUD complet avec gestion des images
- **Gestion des stocks** : Suivi automatique, alertes de stock minimum
- **Paniers et wishlist** : Gestion des paniers utilisateurs et listes de souhaits
- **Commandes** : Workflow complet de commande avec statuts
- **Paiements** : Intégration Stripe pour les paiements en ligne
- **Clients** : Profils clients avec adresses multiples

### 2. **Service** - Services et Support
- **Services** : Abonnements, prestations ponctuelles, consultations
- **Rendez-vous** : Système de réservation avec créneaux disponibles
- **Support technique** : Système de tickets avec messages
- **Abonnements** : Gestion des abonnements récurrents
- **Avis clients** : Système d'évaluation des services

### 3. **Admin Dashboard** - Administration Interne
- **Ressources Humaines** : Employés, départements, congés
- **Comptabilité Belge** : Conforme au PCMN (Plan Comptable Minimum Normalisé)
- **Facturation** : Génération et suivi des factures
- **Déclarations TVA** : Génération automatique des déclarations TVA belges

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

4. **Configuration de la base de données**
```bash
# Créer la base PostgreSQL
createdb ecommerce_db

# Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres
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

8. **Lancer le serveur**
```bash
python manage.py runserver
```

## Endpoints API Principaux

### Authentification
- `POST /api/auth/token/` - Obtenir un token JWT
- `POST /api/auth/token/refresh/` - Rafraîchir le token

### Shop
- `GET /api/shop/products/` - Liste des produits
- `POST /api/shop/cart/{id}/add_item/` - Ajouter au panier
- `POST /api/shop/orders/` - Créer une commande
- `POST /api/shop/orders/{id}/create_payment_intent/` - Paiement Stripe

### Service
- `GET /api/service/services/` - Liste des services
- `POST /api/service/appointments/` - Réserver un rendez-vous
- `POST /api/service/tickets/` - Créer un ticket de support

### Admin Dashboard
- `GET /api/admin-dashboard/employees/` - Gestion des employés
- `POST /api/admin-dashboard/invoices/` - Créer une facture
- `POST /api/admin-dashboard/vat-declarations/generate_declaration/` - Générer déclaration TVA

## Documentation API

La documentation interactive est disponible à :
- **Swagger UI** : `http://localhost:8000/api/docs/`
- **Schema OpenAPI** : `http://localhost:8000/api/schema/`

## Technologies Utilisées

- **Django 5.0** : Framework web Python
- **Django REST Framework** : API REST
- **PostgreSQL** : Base de données
- **JWT** : Authentification
- **Stripe** : Paiements en ligne
- **Celery + Redis** : Tâches asynchrones
- **drf-spectacular** : Documentation API

## Conformité Légale Belge

Le système respecte la législation comptable belge :
- **Arrêté royal du 29 avril 2019** relatif au plan comptable minimum normalisé
- **Code de la TVA** belge pour les taux et déclarations
- **Loi comptable** du 17 juillet 1975 pour la tenue des livres comptables

## Sécurité

- Authentification JWT obligatoire pour les endpoints sensibles
- Permissions granulaires par rôle utilisateur
- Validation des données d'entrée
- Protection CORS configurée
- Variables d'environnement pour les secrets