"""
Script d'optimisations au démarrage de l'application
"""
import os
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
    django.setup()

def warm_cache():
    """Préchauffage du cache au démarrage"""
    print("Préchauffage du cache...")
    
    try:
        from cache_system import CacheManager
        from low_level_optimizations import CacheWarmer
        
        # Préchauffer le cache des produits
        CacheWarmer.warm_product_cache()
        
        # Préchauffer les données fréquemment utilisées
        from shop.models import Category, Product
        
        # Charger les catégories populaires
        categories = Category.objects.filter(is_active=True)[:10]
        for category in categories:
            cache_key = f"category:{category.id}"
            CacheManager.set_cache(cache_key, {
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            }, 7200, 'categories')
        
        print(f"Cache préchauffé pour {len(categories)} catégories")
        
        # Charger les produits populaires
        products = Product.objects.filter(is_active=True)[:20]
        for product in products:
            cache_key = f"product:{product.id}"
            CacheManager.set_cache(cache_key, {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'stock_quantity': product.stock_quantity
            }, 3600, 'products')
        
        print(f"Cache préchauffé pour {len(products)} produits")
        
    except Exception as e:
        print(f"Erreur lors du préchauffage du cache: {e}")

def optimize_database():
    """Optimisations de base de données"""
    print("Optimisation de la base de données...")
    
    try:
        from django.db import connection
        
        # Analyser les tables SQLite
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE")
            
        print("Base de données optimisée")
        
    except Exception as e:
        print(f"Erreur lors de l'optimisation de la base de données: {e}")

def setup_logging():
    """Configuration du logging avancé"""
    print("Configuration du logging...")
    
    try:
        import logging
        
        # Créer les répertoires de logs s'ils n'existent pas
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configuration des loggers
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/application.log'),
                logging.StreamHandler()
            ]
        )
        
        print("Logging configuré")
        
    except Exception as e:
        print(f"Erreur lors de la configuration du logging: {e}")

def check_system_resources():
    """Vérifier les ressources système"""
    print("Vérification des ressources système...")
    
    try:
        from low_level_optimizations import MemoryOptimizer
        import psutil
        
        # Mémoire
        memory_info = MemoryOptimizer.monitor_memory_usage()
        print(f"Mémoire utilisée: {memory_info['rss']:.2f}MB ({memory_info['percent']:.1f}%)")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"CPU: {cpu_percent}%")
        
        # Disque
        disk_usage = psutil.disk_usage('.')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        print(f"Disque: {disk_percent:.1f}% utilisé")
        
        # Avertissements
        if memory_info['percent'] > 80:
            print("[WARNING] Utilisation memoire elevee")
        if cpu_percent > 80:
            print("[WARNING] Utilisation CPU elevee")
        if disk_percent > 90:
            print("[WARNING] Espace disque faible")
            
    except Exception as e:
        print(f"Erreur lors de la vérification des ressources: {e}")

def initialize_async_processor():
    """Initialiser le processeur asynchrone"""
    print("Initialisation du processeur asynchrone...")
    
    try:
        from low_level_optimizations import async_processor
        
        # Test du processeur asynchrone
        def test_task():
            return "Processeur asynchrone opérationnel"
        
        future = async_processor.submit_task(test_task)
        if future:
            result = future.result(timeout=5)
            print(f"[OK] {result}")
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation du processeur asynchrone: {e}")

def main():
    """Fonction principale d'optimisation au démarrage"""
    print("Demarrage des optimisations...")
    print("=" * 50)
    
    # Configuration Django
    setup_django()
    
    # Optimisations
    optimizations = [
        ("Configuration du logging", setup_logging),
        ("Vérification des ressources système", check_system_resources),
        ("Optimisation de la base de données", optimize_database),
        ("Préchauffage du cache", warm_cache),
        ("Initialisation du processeur asynchrone", initialize_async_processor),
    ]
    
    for name, func in optimizations:
        print(f"\n[EXEC] {name}...")
        try:
            func()
            print(f"[OK] {name} termine")
        except Exception as e:
            print(f"[ERREUR] {name}: {e}")
    
    print("\n" + "=" * 50)
    print("Optimisations terminees !")
    print("\nConseils pour de meilleures performances:")
    print("   - Utilisez Redis pour le cache en production")
    print("   - Configurez PostgreSQL pour de gros volumes")
    print("   - Activez la compression gzip")
    print("   - Surveillez les logs de performance")

if __name__ == '__main__':
    main()