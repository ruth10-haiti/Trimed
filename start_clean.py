#!/usr/bin/env python
"""
Démarrage propre de l'application
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Exécuter une commande"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description}: {e.stderr}")
        return False

def main():
    """Démarrage propre"""
    print("=" * 50)
    print("DÉMARRAGE PROPRE - TRIMED BACKEND")
    print("=" * 50)
    
    # 1. Ignorer les migrations et démarrer directement
    print("\n[INFO] Démarrage du serveur sans migrations...")
    print("[INFO] URL: http://127.0.0.1:8000")
    print("[INFO] Documentation: http://127.0.0.1:8000/swagger/")
    print("[INFO] Appuyez sur Ctrl+C pour arrêter")
    
    try:
        # Démarrer le serveur en ignorant les migrations
        os.system("python manage.py runserver 0.0.0.0:8000 --skip-checks")
    except KeyboardInterrupt:
        print("\n[INFO] Serveur arrêté")

if __name__ == "__main__":
    if not os.path.exists('manage.py'):
        print("[ERROR] manage.py non trouvé")
        sys.exit(1)
    
    main()