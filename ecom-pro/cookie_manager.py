"""
Gestionnaire de cookies avancé avec sécurité et performance
"""
import json
import hashlib
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.conf import settings
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class SecureCookieManager:
    """Gestionnaire de cookies sécurisé"""
    
    # Configuration par défaut
    DEFAULT_MAX_AGE = 86400  # 24 heures
    SECURE_COOKIES = getattr(settings, 'SECURE_SSL_REDIRECT', False)
    SAMESITE_POLICY = 'Lax'
    
    @staticmethod
    def set_cookie(response: HttpResponse, key: str, value: Any, 
                   max_age: int = None, secure: bool = None, 
                   httponly: bool = True, samesite: str = None) -> HttpResponse:
        """Définir un cookie sécurisé"""
        try:
            # Sérialiser la valeur si nécessaire
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            # Configuration de sécurité
            max_age = max_age or SecureCookieManager.DEFAULT_MAX_AGE
            secure = secure if secure is not None else SecureCookieManager.SECURE_COOKIES
            samesite = samesite or SecureCookieManager.SAMESITE_POLICY
            
            response.set_cookie(
                key=key,
                value=value,
                max_age=max_age,
                secure=secure,
                httponly=httponly,
                samesite=samesite
            )
            
            logger.debug(f"Cookie set: {key} (max_age: {max_age}s)")
            return response
            
        except Exception as e:
            logger.error(f"Cookie set error for {key}: {e}")
            return response
    
    @staticmethod
    def get_cookie(request, key: str, default: Any = None, parse_json: bool = False) -> Any:
        """Récupérer un cookie"""
        try:
            value = request.COOKIES.get(key, default)
            
            if value and parse_json:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON cookie: {key}")
                    return default
            
            logger.debug(f"Cookie retrieved: {key}")
            return value
            
        except Exception as e:
            logger.error(f"Cookie get error for {key}: {e}")
            return default
    
    @staticmethod
    def delete_cookie(response: HttpResponse, key: str) -> HttpResponse:
        """Supprimer un cookie"""
        try:
            response.delete_cookie(key)
            logger.debug(f"Cookie deleted: {key}")
            return response
        except Exception as e:
            logger.error(f"Cookie delete error for {key}: {e}")
            return response

class UserPreferenceCookies:
    """Gestion des préférences utilisateur via cookies"""
    
    PREFERENCE_KEYS = {
        'language': 'user_lang',
        'theme': 'user_theme',
        'currency': 'user_currency',
        'timezone': 'user_timezone',
        'items_per_page': 'user_items_per_page',
        'dashboard_layout': 'user_dashboard_layout'
    }
    
    @staticmethod
    def set_preference(response: HttpResponse, preference: str, value: Any) -> HttpResponse:
        """Définir une préférence utilisateur"""
        cookie_key = UserPreferenceCookies.PREFERENCE_KEYS.get(preference)
        if not cookie_key:
            logger.warning(f"Unknown preference: {preference}")
            return response
        
        return SecureCookieManager.set_cookie(
            response, cookie_key, value, 
            max_age=86400 * 30,  # 30 jours
            httponly=False  # Accessible en JavaScript pour l'UI
        )
    
    @staticmethod
    def get_preference(request, preference: str, default: Any = None) -> Any:
        """Récupérer une préférence utilisateur"""
        cookie_key = UserPreferenceCookies.PREFERENCE_KEYS.get(preference)
        if not cookie_key:
            return default
        
        return SecureCookieManager.get_cookie(request, cookie_key, default)
    
    @staticmethod
    def get_all_preferences(request) -> Dict[str, Any]:
        """Récupérer toutes les préférences utilisateur"""
        preferences = {}
        for pref, cookie_key in UserPreferenceCookies.PREFERENCE_KEYS.items():
            preferences[pref] = SecureCookieManager.get_cookie(request, cookie_key)
        return preferences

class SessionCookies:
    """Gestion des cookies de session"""
    
    @staticmethod
    def set_session_data(response: HttpResponse, key: str, data: Dict) -> HttpResponse:
        """Définir des données de session"""
        session_key = f"session_{key}"
        return SecureCookieManager.set_cookie(
            response, session_key, data,
            max_age=3600,  # 1 heure
            secure=True,
            httponly=True
        )
    
    @staticmethod
    def get_session_data(request, key: str) -> Optional[Dict]:
        """Récupérer des données de session"""
        session_key = f"session_{key}"
        return SecureCookieManager.get_cookie(
            request, session_key, 
            default=None, parse_json=True
        )
    
    @staticmethod
    def clear_session_data(response: HttpResponse, key: str) -> HttpResponse:
        """Effacer des données de session"""
        session_key = f"session_{key}"
        return SecureCookieManager.delete_cookie(response, session_key)

class CartCookies:
    """Gestion du panier via cookies pour utilisateurs non connectés"""
    
    CART_COOKIE_KEY = 'guest_cart'
    CART_MAX_AGE = 86400 * 7  # 7 jours
    
    @staticmethod
    def set_cart(response: HttpResponse, cart_data: Dict) -> HttpResponse:
        """Définir le panier dans un cookie"""
        return SecureCookieManager.set_cookie(
            response, CartCookies.CART_COOKIE_KEY, cart_data,
            max_age=CartCookies.CART_MAX_AGE,
            httponly=False  # Accessible en JavaScript
        )
    
    @staticmethod
    def get_cart(request) -> Dict:
        """Récupérer le panier depuis un cookie"""
        return SecureCookieManager.get_cookie(
            request, CartCookies.CART_COOKIE_KEY,
            default={'items': [], 'total': 0},
            parse_json=True
        )
    
    @staticmethod
    def add_item_to_cart(request, response: HttpResponse, 
                        product_id: int, quantity: int, price: float) -> HttpResponse:
        """Ajouter un article au panier cookie"""
        cart = CartCookies.get_cart(request)
        
        # Chercher si l'article existe déjà
        for item in cart['items']:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                break
        else:
            # Nouvel article
            cart['items'].append({
                'product_id': product_id,
                'quantity': quantity,
                'price': price
            })
        
        # Recalculer le total
        cart['total'] = sum(item['quantity'] * item['price'] for item in cart['items'])
        
        return CartCookies.set_cart(response, cart)
    
    @staticmethod
    def clear_cart(response: HttpResponse) -> HttpResponse:
        """Vider le panier cookie"""
        return SecureCookieManager.delete_cookie(response, CartCookies.CART_COOKIE_KEY)