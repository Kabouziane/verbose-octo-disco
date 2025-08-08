#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

def test_vat_api():
    """Test de l'API de validation TVA"""
    
    # URL de l'API
    url = "http://localhost:8000/api/shop/customers/validate_vat/"
    
    # Token d'authentification (remplacer par un vrai token)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN_HERE'  # À remplacer
    }
    
    # Test avec votre numéro de TVA
    data = {
        'vat_number': 'BE0874355129'
    }
    
    try:
        print("Test de l'API de validation TVA...")
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('valid'):
                print("[OK] TVA valide!")
                print(f"Entreprise: {result.get('company_name', 'N/A')}")
                print(f"Adresse: {result.get('company_address', 'N/A')}")
            else:
                print(f"[KO] TVA invalide: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"[ERROR] Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")

if __name__ == '__main__':
    test_vat_api()