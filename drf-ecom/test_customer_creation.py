#!/usr/bin/env python
import requests
import json

def test_customer_creation():
    """Test de création client avec base propre"""
    
    url = "http://localhost:8000/api/shop/customers/create_customer/"
    
    # Test 1: Client particulier
    data1 = {
        "first_name": "Jean",
        "last_name": "Dupont", 
        "email": "jean.dupont@test.com",
        "phone": "0123456789",
        "is_business": False
    }
    
    # Test 2: Client entreprise
    data2 = {
        "email": "contact@entreprise.com",
        "phone": "0987654321", 
        "is_business": True,
        "company_name": "Test Entreprise SARL",
        "company_address": "123 Rue de Test\n1000 Bruxelles",
        "vat_number": "BE0123456789",
        "iban": "BE68 5390 0754 7034"
    }
    
    tests = [
        ("Particulier", data1),
        ("Entreprise", data2)
    ]
    
    for test_name, data in tests:
        print(f"\n=== TEST {test_name} ===")
        print(f"Données: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(url, json=data, timeout=10)
            print(f"Status: {response.status_code}")
            
            result = response.json()
            print(f"Réponse: {json.dumps(result, indent=2)}")
            
            if response.status_code == 201:
                print("✅ SUCCÈS")
            else:
                print("❌ ÉCHEC")
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")

if __name__ == '__main__':
    test_customer_creation()