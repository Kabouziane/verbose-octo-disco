#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import sys

def check_frontend():
    """Vérification de l'état du frontend Vue.js"""
    
    frontend_path = "frontend"
    
    print("=== DEBUG FRONTEND ===\n")
    
    # 1. Vérifier si le dossier frontend existe
    if not os.path.exists(frontend_path):
        print("[ERROR] Dossier frontend introuvable!")
        return
    
    print("[OK] Dossier frontend trouvé")
    
    # 2. Vérifier package.json
    package_json = os.path.join(frontend_path, "package.json")
    if os.path.exists(package_json):
        print("[OK] package.json trouvé")
    else:
        print("[ERROR] package.json manquant!")
        return
    
    # 3. Vérifier node_modules
    node_modules = os.path.join(frontend_path, "node_modules")
    if os.path.exists(node_modules):
        print("[OK] node_modules trouvé")
    else:
        print("[WARNING] node_modules manquant - exécuter 'npm install'")
    
    # 4. Vérifier les fichiers Vue
    vue_files = [
        "src/views/Login.vue",
        "src/views/Dashboard.vue", 
        "src/views/Invoices.vue",
        "src/views/Customers.vue",
        "src/views/VAT.vue"
    ]
    
    for vue_file in vue_files:
        full_path = os.path.join(frontend_path, vue_file)
        if os.path.exists(full_path):
            print(f"[OK] {vue_file}")
        else:
            print(f"[ERROR] {vue_file} manquant!")
    
    # 5. Vérifier le routeur
    router_file = os.path.join(frontend_path, "src/router/index.js")
    if os.path.exists(router_file):
        print("[OK] Router configuré")
    else:
        print("[ERROR] Router manquant!")
    
    print("\n=== COMMANDES POUR DÉMARRER ===")
    print("1. cd frontend")
    print("2. npm install (si node_modules manquant)")
    print("3. npm run dev")
    print("\n=== SERVEUR DJANGO ===")
    print("1. env\\Scripts\\activate")
    print("2. python manage.py runserver")

if __name__ == '__main__':
    check_frontend()