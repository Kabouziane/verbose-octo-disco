"""
Configuration et utilitaires de cache avancés
"""
import hashlib
import json
from django.core.cache import cache
from django.conf import settings
from functools import wraps
from typing import Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestionnaire de cache avancé"""
    
    # Durées de cache par défaut (en secondes)
    CACHE_TIMEOUTS = {
        'products': 3600,  # 1 heure
        'categories': 7200,  # 2 heures
        'customers': 1800,  # 30 minutes
        'invoices': 900,   # 15 minutes
        'services': 3600,  # 1 heure
        'accounting': 1800,  # 30 minutes
        'vat_rates': 86400,  # 24 heures
        'user_session': 3600,  # 1 heure
    }
    
    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """Générer une clé de cache unique"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    @staticmethod
    def set_cache(key: str, value: Any, timeout: Optional[int] = None, category: str = 'default') -> bool:
        """Mettre en cache une valeur"""
        try:
            if timeout is None:
                timeout = CacheManager.CACHE_TIMEOUTS.get(category, 3600)
            
            cache.set(key, value, timeout)
            logger.debug(f"Cache set: {key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            return False
    
    @staticmethod
    def get_cache(key: str, default: Any = None) -> Any:
        """Récupérer une valeur du cache"""
        try:
            value = cache.get(key, default)
            if value is not None:
                logger.debug(f"Cache hit: {key}")
            else:
                logger.debug(f"Cache miss: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            return default
    
    @staticmethod
    def delete_cache(key: str) -> bool:
        """Supprimer une clé du cache"""
        try:
            cache.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            return False

def cache_result(timeout: int = 3600, category: str = 'default', key_prefix: str = None):
    """Décorateur pour mettre en cache le résultat d'une fonction"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé de cache
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = CacheManager.generate_cache_key(prefix, *args, **kwargs)
            
            # Vérifier le cache
            cached_result = CacheManager.get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Exécuter la fonction et mettre en cache
            result = func(*args, **kwargs)
            CacheManager.set_cache(cache_key, result, timeout, category)
            
            return result
        return wrapper
    return decorator