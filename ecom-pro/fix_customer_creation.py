#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Customer

def fix_orphaned_user():
    """Créer un profil client pour l'utilisateur karim"""
    
    try:
        user = User.objects.get(username='karim')
        
        if hasattr(user, 'customer'):
            print("L'utilisateur karim a déjà un profil client")
            return
        
        # Créer le profil client manquant
        customer = Customer.objects.create(
            user=user,
            phone='',
            is_business=False,
            company_name='',
            company_address='',
            vat_number='',
            iban=''
        )
        
        print(f"Profil client créé pour karim: ID {customer.id}")
        
    except User.DoesNotExist:
        print("Utilisateur karim non trouvé")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == '__main__':
    fix_orphaned_user()