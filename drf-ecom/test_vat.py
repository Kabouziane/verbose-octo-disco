#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from shop.vat_validator import validate_vat_number

def test_vat_numbers():
    """Test de différents numéros de TVA"""
    
    test_cases = [
        # Votre numéro
        "BE 0874.355.129",
        "BE0874355129",
        
        # Numéros belges connus
        "BE0417497106",  # Microsoft Belgium
        "BE0403170701",  # Google Belgium
        
        # Numéros invalides
        "BE1234567890",
        "FR12345678901",
        
        # Formats incorrects
        "BE123",
        "INVALID",
        ""
    ]
    
    print("=== TEST VALIDATION TVA ===\n")
    
    for vat_num in test_cases:
        print(f"Test: '{vat_num}'")
        result = validate_vat_number(vat_num)
        
        if result['valid']:
            print("[OK] VALIDE")
            print(f"   Entreprise: {result.get('company_name', 'N/A')}")
            print(f"   Adresse: {result.get('company_address', 'N/A')}")
        else:
            print(f"[KO] INVALIDE: {result.get('error', 'Erreur inconnue')}")
        
        print("-" * 50)

if __name__ == '__main__':
    test_vat_numbers()