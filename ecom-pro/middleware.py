"""
Middleware personnalisés pour optimisations et fonctionnalités avancées
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from cache_system import CacheManager, SessionCache
from cookie_manager import SecureCookieManager, UserPreferenceCookies
from low_level_optimizations import PerformanceMonitor, MemoryOptimizer

logger = logging.getLogger(__name__)

class PerformanceMiddleware(MiddlewareMixin):
    """Middleware pour surveiller les performances"""
    
    def process_request(self, request):
        """Démarrer le chronométrage"""
        request._start_time = time.time()
        request._memory_before = MemoryOptimizer.monitor_memory_usage()
        
        # Log de la requête
        logger.debug(f"Request started: {request.method} {request.path}")
        
        return None
    
    def process_response(self, request, response):
        """Finaliser le chronométrage et ajouter les headers"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Ajouter les headers de performance
            response['X-Response-Time'] = f"{duration:.4f}s"
            response['X-Memory-Usage'] = f"{request._memory_before['rss']:.2f}MB"
            
            # Log des performances
            if duration > 1.0:  # Requêtes lentes > 1s
                logger.warning(f"Slow request: {request.method} {request.path} - {duration:.4f}s")
            else:
                logger.debug(f"Request completed: {request.method} {request.path} - {duration:.4f}s")
            
            # Stocker les métriques en cache
            cache_key = f"perf_metrics:{request.path}"
            metrics = cache.get(cache_key, [])
            metrics.append({
                'timestamp': time.time(),
                'duration': duration,
                'method': request.method,
                'status_code': response.status_code
            })
            
            # Garder seulement les 50 dernières mesures
            if len(metrics) > 50:
                metrics = metrics[-50:]
            
            cache.set(cache_key, metrics, 3600)
        
        return response

class CacheMiddleware(MiddlewareMixin):
    """Middleware pour la gestion du cache"""
    
    CACHEABLE_METHODS = ['GET']
    CACHE_PATHS = ['/api/shop/products/', '/api/shop/categories/', '/api/service/services/']
    
    def process_request(self, request):
        """Vérifier le cache avant de traiter la requête"""
        if (request.method in self.CACHEABLE_METHODS and 
            any(request.path.startswith(path) for path in self.CACHE_PATHS)):
            
            cache_key = CacheManager.generate_cache_key(
                'middleware_cache', 
                request.path, 
                request.GET.dict()
            )
            
            cached_response = CacheManager.get_cache(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {request.path}")
                return JsonResponse(cached_response)
        
        return None
    
    def process_response(self, request, response):
        """Mettre en cache la réponse si applicable"""
        if (request.method in self.CACHEABLE_METHODS and 
            any(request.path.startswith(path) for path in self.CACHE_PATHS) and
            response.status_code == 200):
            
            try:
                cache_key = CacheManager.generate_cache_key(
                    'middleware_cache', 
                    request.path, 
                    request.GET.dict()
                )
                
                # Essayer de parser le JSON pour le mettre en cache
                if hasattr(response, 'content'):
                    import json
                    response_data = json.loads(response.content.decode('utf-8'))
                    CacheManager.set_cache(cache_key, response_data, 1800, 'api_responses')
                    logger.debug(f"Response cached for {request.path}")
                    
            except Exception as e:
                logger.error(f"Cache middleware error: {e}")
        
        return response

class UserPreferenceMiddleware(MiddlewareMixin):
    """Middleware pour gérer les préférences utilisateur via cookies"""
    
    def process_request(self, request):
        """Charger les préférences utilisateur"""
        # Charger toutes les préférences dans request.user_preferences
        request.user_preferences = UserPreferenceCookies.get_all_preferences(request)
        
        # Définir des valeurs par défaut
        defaults = {
            'language': 'fr',
            'theme': 'light',
            'currency': 'EUR',
            'timezone': 'Europe/Brussels',
            'items_per_page': 20
        }
        
        for key, default_value in defaults.items():
            if not request.user_preferences.get(key):
                request.user_preferences[key] = default_value
        
        return None
    
    def process_response(self, request, response):
        """Sauvegarder les préférences modifiées"""
        # Vérifier s'il y a des préférences à sauvegarder
        if hasattr(request, '_preferences_to_save'):
            for pref, value in request._preferences_to_save.items():
                UserPreferenceCookies.set_preference(response, pref, value)
        
        return response

class SecurityMiddleware(MiddlewareMixin):
    """Middleware de sécurité avancé"""
    
    def process_response(self, request, response):
        """Ajouter les headers de sécurité"""
        # Headers de sécurité
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:;"
        )
        response['Content-Security-Policy'] = csp
        
        return response

class RateLimitMiddleware(MiddlewareMixin):
    """Middleware de limitation de taux"""
    
    def process_request(self, request):
        """Vérifier les limites de taux"""
        # Obtenir l'IP du client
        client_ip = self.get_client_ip(request)
        
        # Clé de cache pour le rate limiting
        cache_key = f"rate_limit:{client_ip}"
        
        # Récupérer le compteur actuel
        current_requests = cache.get(cache_key, 0)
        
        # Limite: 100 requêtes par minute
        if current_requests >= 100:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)
        
        # Incrémenter le compteur
        cache.set(cache_key, current_requests + 1, 60)  # 60 secondes
        
        return None
    
    def get_client_ip(self, request):
        """Obtenir l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class DatabaseOptimizationMiddleware(MiddlewareMixin):
    """Middleware pour optimiser les requêtes de base de données"""
    
    def process_request(self, request):
        """Initialiser le compteur de requêtes"""
        from django.db import connection
        request._queries_before = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Analyser les requêtes de base de données"""
        if hasattr(request, '_queries_before'):
            from django.db import connection
            queries_count = len(connection.queries) - request._queries_before
            
            # Ajouter le header avec le nombre de requêtes
            response['X-DB-Queries'] = str(queries_count)
            
            # Log des requêtes excessives
            if queries_count > 10:
                logger.warning(f"High DB query count: {queries_count} for {request.path}")
            
            # En mode debug, ajouter les détails des requêtes
            if hasattr(request, '_start_time') and queries_count > 0:
                total_time = sum(float(q['time']) for q in connection.queries[-queries_count:])
                response['X-DB-Time'] = f"{total_time:.4f}s"
        
        return response

class CompressionMiddleware(MiddlewareMixin):
    """Middleware de compression des réponses"""
    
    def process_response(self, request, response):
        """Ajouter les headers de compression"""
        # Indiquer que la compression est supportée
        if 'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', ''):
            response['Vary'] = 'Accept-Encoding'
        
        return response