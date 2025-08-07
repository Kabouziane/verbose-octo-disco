import requests
import re
from typing import Dict, Optional

def validate_vat_number(vat_number: str) -> Dict:
    """
    Valide un numéro de TVA via l'API VIES officielle
    """
    # Nettoyer le numéro de TVA
    clean_vat = re.sub(r'[^A-Z0-9]', '', vat_number.upper())
    
    if not clean_vat:
        return {
            'valid': False,
            'error': 'Numéro de TVA vide'
        }
    
    # Extraire le code pays et le numéro
    if len(clean_vat) < 3:
        return {
            'valid': False,
            'error': 'Numéro de TVA trop court'
        }
    
    country_code = clean_vat[:2]
    vat_num = clean_vat[2:]
    
    try:
        # Utilisation de l'API VIES officielle (REST)
        vies_url = f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country_code}/vat/{vat_num}"
        
        response = requests.get(vies_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('isValid', False):
                return {
                    'valid': True,
                    'vat_number': clean_vat,
                    'country_code': country_code,
                    'company_name': data.get('name', ''),
                    'company_address': data.get('address', ''),
                    'request_date': data.get('requestDate', ''),
                    'source': 'VIES'
                }
            else:
                return {
                    'valid': False,
                    'error': 'Numéro de TVA invalide selon VIES'
                }
        elif response.status_code == 400:
            return {
                'valid': False,
                'error': 'Format de numéro de TVA invalide'
            }
        else:
            # Fallback: validation basique du format
            return validate_vat_format(clean_vat)
            
    except requests.RequestException as e:
        print(f"Erreur VIES: {e}")
        # En cas d'erreur réseau, validation du format seulement
        return validate_vat_format(clean_vat)

def validate_vat_format(vat_number: str) -> Dict:
    """
    Validation basique du format des numéros de TVA européens
    """
    patterns = {
        'BE': r'^BE[0-9]{10}$',  # Belgique
        'FR': r'^FR[A-Z0-9]{2}[0-9]{9}$',  # France
        'DE': r'^DE[0-9]{9}$',  # Allemagne
        'NL': r'^NL[0-9]{9}B[0-9]{2}$',  # Pays-Bas
        'IT': r'^IT[0-9]{11}$',  # Italie
        'ES': r'^ES[A-Z0-9][0-9]{7}[A-Z0-9]$',  # Espagne
        'GB': r'^GB[0-9]{9}$|^GB[0-9]{12}$|^GBGD[0-9]{3}$|^GBHA[0-9]{3}$',  # Royaume-Uni
    }
    
    country_code = vat_number[:2]
    
    if country_code in patterns:
        if re.match(patterns[country_code], vat_number):
            return {
                'valid': True,
                'vat_number': vat_number,
                'country_code': country_code,
                'format_valid': True,
                'note': 'Format valide - vérification en ligne non disponible'
            }
    
    return {
        'valid': False,
        'error': 'Format de numéro de TVA invalide'
    }