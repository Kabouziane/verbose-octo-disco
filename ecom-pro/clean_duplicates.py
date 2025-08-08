#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from shop.models import Customer
from django.contrib.auth.models import User
from collections import defaultdict

def clean_duplicates():
    """Nettoyer les clients en double"""
    
    # Grouper par email
    email_groups = defaultdict(list)
    for customer in Customer.objects.all():
        email_groups[customer.user.email].append(customer)
    
    print(f"Total clients: {Customer.objects.count()}")
    
    # Supprimer les doublons
    for email, customers in email_groups.items():
        if len(customers) > 1:
            print(f"Email {email}: {len(customers)} doublons")
            # Garder le premier, supprimer les autres
            for customer in customers[1:]:
                print(f"  Suppression client ID {customer.id}")
                customer.delete()
    
    print(f"Clients après nettoyage: {Customer.objects.count()}")

if __name__ == '__main__':
    clean_duplicates()