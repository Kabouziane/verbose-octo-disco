#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Customer

def fix_login():
    """Corriger le problème de connexion"""
    
    try:
        # Vérifier si l'utilisateur karim existe
        user = User.objects.get(username='karim')
        print(f"Utilisateur trouvé: {user.username}")
        print(f"Email: {user.email}")
        print(f"Est superuser: {user.is_superuser}")
        print(f"Est actif: {user.is_active}")
        
        # Vérifier le profil client
        if hasattr(user, 'customer'):
            print("Profil client: OUI")
        else:
            print("Profil client: NON - Création...")
            Customer.objects.create(
                user=user,
                is_business=False,
                phone='',
                company_name='',
                company_address='',
                vat_number='',
                iban=''
            )
            print("Profil client créé!")
        
        # Réinitialiser le mot de passe
        user.set_password('123')
        user.save()
        print("Mot de passe réinitialisé à '123'")
        
    except User.DoesNotExist:
        print("Utilisateur karim non trouvé - Création...")
        user = User.objects.create_superuser('karim', 'karim@example.com', '123')
        Customer.objects.create(
            user=user,
            is_business=False,
            phone='',
            company_name='',
            company_address='',
            vat_number='',
            iban=''
        )
        print("Utilisateur et profil client créés!")

if __name__ == '__main__':
    fix_login()