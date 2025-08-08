"""
Optimisations low-level pour améliorer les performances
"""
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
import psutil
import logging
from typing import List, Dict, Any, Callable
from functools import wraps
import gc

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Optimisations de base de données"""
    
    @staticmethod
    def bulk_create_optimized(model_class, objects: List[Dict], batch_size: int = 1000):
        """Création en lot optimisée"""
        try:
            model_objects = [model_class(**obj) for obj in objects]
            
            # Traitement par lots pour éviter les timeouts
            for i in range(0, len(model_objects), batch_size):
                batch = model_objects[i:i + batch_size]
                model_class.objects.bulk_create(batch, ignore_conflicts=True)
                
            logger.info(f"Bulk created {len(objects)} {model_class.__name__} objects")
            return True
            
        except Exception as e:
            logger.error(f"Bulk create error: {e}")
            return False
    
    @staticmethod
    def bulk_update_optimized(model_class, objects: List, fields: List[str], batch_size: int = 1000):
        """Mise à jour en lot optimisée"""
        try:
            # Traitement par lots
            for i in range(0, len(objects), batch_size):
                batch = objects[i:i + batch_size]
                model_class.objects.bulk_update(batch, fields)
                
            logger.info(f"Bulk updated {len(objects)} {model_class.__name__} objects")
            return True
            
        except Exception as e:
            logger.error(f"Bulk update error: {e}")
            return False
    
    @staticmethod
    def execute_raw_query(query: str, params: List = None) -> List[Dict]:
        """Exécution de requête SQL brute optimisée"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or [])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
            logger.debug(f"Raw query executed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Raw query error: {e}")
            return []

class MemoryOptimizer:
    """Optimisations mémoire"""
    
    @staticmethod
    def monitor_memory_usage():
        """Surveiller l'utilisation mémoire"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def force_garbage_collection():
        """Forcer le garbage collection"""
        collected = gc.collect()
        logger.debug(f"Garbage collection: {collected} objects collected")
        return collected
    
    @staticmethod
    def memory_efficient_queryset(queryset, chunk_size: int = 1000):
        """Iterator pour traiter de gros querysets sans surcharger la mémoire"""
        try:
            total_count = queryset.count()
            processed = 0
            
            while processed < total_count:
                chunk = queryset[processed:processed + chunk_size]
                for obj in chunk:
                    yield obj
                processed += chunk_size
                
                # Forcer le garbage collection périodiquement
                if processed % (chunk_size * 10) == 0:
                    MemoryOptimizer.force_garbage_collection()
                    
        except Exception as e:
            logger.error(f"Memory efficient queryset error: {e}")

class AsyncProcessor:
    """Traitement asynchrone pour les tâches lourdes"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def submit_task(self, func: Callable, *args, **kwargs):
        """Soumettre une tâche asynchrone"""
        try:
            future = self.executor.submit(func, *args, **kwargs)
            logger.debug(f"Async task submitted: {func.__name__}")
            return future
        except Exception as e:
            logger.error(f"Async task submission error: {e}")
            return None
    
    def process_batch_async(self, func: Callable, items: List, batch_size: int = 100):
        """Traiter une liste d'éléments en parallèle"""
        futures = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            future = self.submit_task(func, batch)
            if future:
                futures.append(future)
        
        # Attendre tous les résultats
        results = []
        for future in futures:
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                logger.error(f"Async batch processing error: {e}")
        
        return results
    
    def shutdown(self):
        """Arrêter l'executor"""
        self.executor.shutdown(wait=True)

class PerformanceMonitor:
    """Moniteur de performance"""
    
    @staticmethod
    def measure_execution_time(func):
        """Décorateur pour mesurer le temps d'exécution"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} executed in {execution_time:.4f}s")
            
            # Stocker les métriques en cache
            cache_key = f"perf_metrics:{func.__name__}"
            metrics = cache.get(cache_key, [])
            metrics.append({
                'timestamp': time.time(),
                'execution_time': execution_time,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            })
            
            # Garder seulement les 100 dernières mesures
            if len(metrics) > 100:
                metrics = metrics[-100:]
            
            cache.set(cache_key, metrics, 3600)  # 1 heure
            
            return result
        return wrapper
    
    @staticmethod
    def get_performance_stats(func_name: str) -> Dict:
        """Récupérer les statistiques de performance"""
        cache_key = f"perf_metrics:{func_name}"
        metrics = cache.get(cache_key, [])
        
        if not metrics:
            return {}
        
        execution_times = [m['execution_time'] for m in metrics]
        
        return {
            'count': len(metrics),
            'avg_time': sum(execution_times) / len(execution_times),
            'min_time': min(execution_times),
            'max_time': max(execution_times),
            'last_execution': metrics[-1]['timestamp'] if metrics else None
        }

class ConnectionPoolOptimizer:
    """Optimiseur de pool de connexions"""
    
    @staticmethod
    def optimize_db_connections():
        """Optimiser les connexions de base de données"""
        try:
            # Fermer les connexions inutilisées
            connection.close()
            
            # Statistiques de connexion
            queries_count = len(connection.queries)
            logger.debug(f"Database queries executed: {queries_count}")
            
            return {
                'queries_count': queries_count,
                'connection_closed': True
            }
            
        except Exception as e:
            logger.error(f"Connection optimization error: {e}")
            return {'error': str(e)}

class CacheWarmer:
    """Préchauffage du cache"""
    
    @staticmethod
    def warm_product_cache():
        """Préchauffer le cache des produits"""
        from shop.models import Product, Category
        
        try:
            # Charger les catégories populaires
            categories = Category.objects.filter(is_active=True)[:10]
            for category in categories:
                cache_key = f"category_products:{category.id}"
                products = Product.objects.filter(category=category, is_active=True)[:20]
                cache.set(cache_key, list(products.values()), 3600)
            
            logger.info("Product cache warmed")
            return True
            
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
            return False
    
    @staticmethod
    def warm_user_cache(user_id: int):
        """Préchauffer le cache utilisateur"""
        try:
            from shop.models import Customer, Cart
            from django.contrib.auth.models import User
            
            # Charger les données utilisateur fréquemment utilisées
            user = User.objects.get(id=user_id)
            customer = Customer.objects.filter(user=user).first()
            cart = Cart.objects.filter(user=user).first()
            
            # Mettre en cache
            cache.set(f"user_data:{user_id}", {
                'user': user,
                'customer': customer,
                'cart': cart
            }, 1800)  # 30 minutes
            
            logger.debug(f"User cache warmed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"User cache warming error: {e}")
            return False

# Instance globale du processeur asynchrone
async_processor = AsyncProcessor()

# Décorateurs utilitaires
def optimize_memory(func):
    """Décorateur pour optimiser la mémoire"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Mesurer la mémoire avant
        memory_before = MemoryOptimizer.monitor_memory_usage()
        
        result = func(*args, **kwargs)
        
        # Forcer le garbage collection
        MemoryOptimizer.force_garbage_collection()
        
        # Mesurer la mémoire après
        memory_after = MemoryOptimizer.monitor_memory_usage()
        
        logger.debug(f"Memory usage - Before: {memory_before['rss']:.2f}MB, After: {memory_after['rss']:.2f}MB")
        
        return result
    return wrapper