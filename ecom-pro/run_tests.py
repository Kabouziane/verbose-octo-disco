#!/usr/bin/env python
"""
Script pour exécuter tous les tests et vérifier l'état de l'application
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

def run_tests():
    """Exécuter tous les tests"""
    print("Execution des tests...")
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_ecom.settings')
    django.setup()
    
    # Exécuter les tests
    test_commands = [
        ['python', 'manage.py', 'test', 'shop.tests', '-v', '2'],
        ['python', 'manage.py', 'test', 'service.tests', '-v', '2'],
        ['python', 'manage.py', 'test', 'admin_dashboard.tests', '-v', '2'],
    ]
    
    all_passed = True
    
    for cmd in test_commands:
        print(f"\nExecution: {' '.join(cmd)}")
        result = os.system(' '.join(cmd))
        if result != 0:
            all_passed = False
            print(f"[ECHEC] Tests: {' '.join(cmd)}")
        else:
            print(f"[OK] Tests: {' '.join(cmd)}")
    
    return all_passed

def check_migrations():
    """Vérifier les migrations"""
    print("\nVerification des migrations...")
    
    # Vérifier les migrations en attente
    result = os.system('python manage.py showmigrations --plan')
    if result == 0:
        print("[OK] Migrations verifiees")
        return True
    else:
        print("[ECHEC] Probleme avec les migrations")
        return False

def check_static_files():
    """Vérifier les fichiers statiques"""
    print("\nVerification des fichiers statiques...")
    
    # Collecter les fichiers statiques
    result = os.system('python manage.py collectstatic --noinput --dry-run')
    if result == 0:
        print("[OK] Fichiers statiques")
        return True
    else:
        print("[ECHEC] Probleme avec les fichiers statiques")
        return False

def check_admin_setup():
    """Vérifier la configuration admin"""
    print("\nVerification de la configuration admin...")
    
    try:
        from django.contrib.auth.models import User
        admin_exists = User.objects.filter(is_superuser=True).exists()
        
        if admin_exists:
            print("[OK] Compte administrateur configure")
            return True
        else:
            print("[WARNING] Aucun compte administrateur trouve")
            print("   Exécutez: python manage.py createsuperuser")
            return False
    except Exception as e:
        print(f"[ECHEC] Erreur verification admin: {e}")
        return False

def check_database():
    """Vérifier la base de données"""
    print("\nVerification de la base de donnees...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result:
            print("[OK] Connexion base de donnees")
            return True
        else:
            print("[ECHEC] Probleme connexion base de donnees")
            return False
    except Exception as e:
        print(f"[ECHEC] Erreur base de donnees: {e}")
        return False

def main():
    """Fonction principale"""
    print("Verification complete de l'application DRF E-commerce")
    print("=" * 60)
    
    checks = [
        ("Base de données", check_database),
        ("Migrations", check_migrations),
        ("Configuration admin", check_admin_setup),
        ("Fichiers statiques", check_static_files),
        ("Tests", run_tests),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n[CHECK] {check_name}...")
        results[check_name] = check_func()
    
    # Résumé final
    print("\n" + "=" * 60)
    print("RESUME FINAL")
    print("=" * 60)
    
    all_good = True
    for check_name, result in results.items():
        status = "[OK]" if result else "[ECHEC]"
        print(f"{check_name:.<30} {status}")
        if not result:
            all_good = False
    
    print("\n" + "=" * 60)
    
    if all_good:
        print("TOUT EST PRET ! L'application est operationnelle.")
        print("\nPour demarrer l'application:")
        print("   1. python manage.py runserver")
        print("   2. Ouvrir http://localhost:8000/api/docs/ pour la documentation")
        print("   3. Frontend disponible dans le dossier 'frontend/'")
        
        print("\nFonctionnalites disponibles:")
        print("   - E-commerce (produits, commandes, paiements)")
        print("   - Services (abonnements, rendez-vous, support)")
        print("   - Administration (RH, comptabilite, facturation)")
        print("   - Facturation belge (TVA, PCMN)")
        print("   - Gestion clients (B2B/B2C)")
        
    else:
        print("ATTENTION : Certains problemes doivent etre resolus.")
        print("   Consultez les messages d'erreur ci-dessus.")
    
    return 0 if all_good else 1

if __name__ == '__main__':
    sys.exit(main())