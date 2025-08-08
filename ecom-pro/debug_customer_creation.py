#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Customer
from shop.customer_serializers import CustomerCreateSerializer

def debug_customer_creation():
    """Debug complet de la création de clients"""
    
    print("=== DEBUG CRÉATION CLIENT ===\n")
    
    # 1. État actuel de la base
    print(f"Utilisateurs existants: {User.objects.count()}")
    print(f"Clients existants: {Customer.objects.count()}")
    
    # 2. Lister les utilisateurs sans client
    users_without_customer = User.objects.filter(customer__isnull=True)
    print(f"Utilisateurs sans client: {users_without_customer.count()}")
    
    for user in users_without_customer:
        print(f"  - {user.username} ({user.email})")
    
    # 3. Test de création
    test_data = {
        'first_name': 'Test',
        'last_name': 'Debug',
        'email': 'test.debug@example.com',
        'is_business': False
    }
    
    print(f"\n=== TEST CRÉATION ===")
    print(f"Données: {test_data}")
    
    serializer = CustomerCreateSerializer(data=test_data)
    
    if serializer.is_valid():
        try:
            customer = serializer.save()
            print(f"✅ Client créé: ID {customer.id}")
            print(f"   Utilisateur: {customer.user.username}")
            print(f"   Email: {customer.user.email}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
    else:
        print(f"❌ Erreurs de validation: {serializer.errors}")
    
    # 4. État final
    print(f"\n=== ÉTAT FINAL ===")
    print(f"Utilisateurs: {User.objects.count()}")
    print(f"Clients: {Customer.objects.count()}")

def cleanup_orphaned_users():
    """Nettoyer les utilisateurs orphelins"""
    print("\n=== NETTOYAGE ===")
    
    # Supprimer les utilisateurs sans client (sauf superuser)
    orphaned = User.objects.filter(customer__isnull=True, is_superuser=False)
    count = orphaned.count()
    
    if count > 0:
        print(f"Suppression de {count} utilisateurs orphelins...")
        orphaned.delete()
        print("✅ Nettoyage terminé")
    else:
        print("Aucun utilisateur orphelin trouvé")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'cleanup':
        cleanup_orphaned_users()
    else:
        debug_customer_creation()