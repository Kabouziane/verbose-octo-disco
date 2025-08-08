#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from shop.vat_validator import validate_vat_number

def test_vat():
    """Test simple de validation TVA"""
    
    test_numbers = [
        'BE0874355129',
        'BE0427572733',
        'BE0123456789',  # Invalide
        'FR12345678901',  # Format français
    ]
    
    for vat in test_numbers:
        print(f"\n=== Test: {vat} ===")
        result = validate_vat_number(vat)
        print(f"Résultat: {result}")

if __name__ == '__main__':
    test_vat()