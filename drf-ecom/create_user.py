#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Customer

def create_user():
    # Créer l'utilisateur
    user, created = User.objects.get_or_create(
        username='karim',
        defaults={
            'email': 'karim@example.com',
            'first_name': 'Karim',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        user.set_password('123')
        user.save()
        print(f"✅ Utilisateur '{user.username}' créé avec succès")
    else:
        user.set_password('123')
        user.save()
        print(f"✅ Mot de passe mis à jour pour '{user.username}'")
    
    # Créer le profil client
    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            'phone': '+32 123 456 789',
            'is_business': True
        }
    )
    
    if created:
        print(f"✅ Profil client créé pour '{user.username}'")
    else:
        print(f"✅ Profil client existe déjà pour '{user.username}'")

if __name__ == '__main__':
    create_user()