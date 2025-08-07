import requests
import re
from typing import Dict
import xml.etree.ElementTree as ET

def validate_vat_number(vat_number: str) -> Dict:
    """
    Valide un numéro de TVA via l'API VIES SOAP
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
    
    print(f"Test VIES pour: {country_code} - {vat_num}")
    
    try:
        # SOAP request pour VIES
        soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns1="urn:ec.europa.eu:taxud:vies:services:checkVat:types">
    <soap:Header>
    </soap:Header>
    <soap:Body>
        <tns1:checkVat>
            <tns1:countryCode>{country_code}</tns1:countryCode>
            <tns1:vatNumber>{vat_num}</tns1:vatNumber>
        </tns1:checkVat>
    </soap:Body>
</soap:Envelope>"""

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }
        
        response = requests.post(
            'https://ec.europa.eu/taxation_customs/vies/services/checkVatService',
            data=soap_body,
            headers=headers,
            timeout=15
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Parser la réponse XML
            root = ET.fromstring(response.content)
            
            # Namespaces
            ns = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'tns1': 'urn:ec.europa.eu:taxud:vies:services:checkVat:types'
            }
            
            valid_elem = root.find('.//tns1:valid', ns)
            name_elem = root.find('.//tns1:name', ns)
            address_elem = root.find('.//tns1:address', ns)
            
            print(f"Valid element: {valid_elem.text if valid_elem is not None else 'None'}")
            
            if valid_elem is not None and valid_elem.text == 'true':
                return {
                    'valid': True,
                    'vat_number': clean_vat,
                    'country_code': country_code,
                    'company_name': name_elem.text if name_elem is not None else '',
                    'company_address': address_elem.text if address_elem is not None else '',
                    'source': 'VIES SOAP'
                }
            else:
                return {
                    'valid': False,
                    'error': 'Numéro de TVA invalide selon VIES'
                }
        else:
            print(f"Erreur HTTP: {response.status_code}")
            return validate_vat_format(clean_vat)
            
    except Exception as e:
        print(f"Erreur VIES SOAP: {e}")
        return validate_vat_format(clean_vat)

def validate_vat_format(vat_number: str) -> Dict:
    """
    Validation basique du format des numéros de TVA européens
    """
    patterns = {
        'BE': r'^BE[0-9]{10}$',
        'FR': r'^FR[A-Z0-9]{2}[0-9]{9}$',
        'DE': r'^DE[0-9]{9}$',
        'NL': r'^NL[0-9]{9}B[0-9]{2}$',
        'IT': r'^IT[0-9]{11}$',
        'ES': r'^ES[A-Z0-9][0-9]{7}[A-Z0-9]$',
        'GB': r'^GB[0-9]{9}$|^GB[0-9]{12}$',
    }
    
    country_code = vat_number[:2]
    
    if country_code in patterns:
        if re.match(patterns[country_code], vat_number):
            return {
                'valid': True,
                'vat_number': vat_number,
                'country_code': country_code,
                'company_name': '',
                'note': 'Format valide - vérification VIES non disponible'
            }
    
    return {
        'valid': False,
        'error': 'Format de numéro de TVA invalide'
    }