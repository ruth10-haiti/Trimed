#!/usr/bin/env python
"""
Script pour réinitialiser complètement la base de données
"""
import os
import sys
import subprocess
import psycopg2

def reset_database():
    """Réinitialiser la base de données PostgreSQL"""
    
    print("[INFO] Réinitialisation de la base de données...")
    
    # Paramètres de connexion
    config = {
        'host': 'localhost',
        'port': '5432',
        'user': 'admin_Trimedh',
        'password': 'root'
    }
    
    try:
        # Connexion à PostgreSQL (sans spécifier la base)
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database='postgres'  # Base par défaut
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Supprimer la base existante
        print("[INFO] Suppression de la base existante...")
        cursor.execute("DROP DATABASE IF EXISTS \"Trimedh_BD\";")
        
        # Recréer la base
        print("[INFO] Création de la nouvelle base...")
        cursor.execute("CREATE DATABASE \"Trimedh_BD\" OWNER admin_Trimedh;")
        
        cursor.close()
        conn.close()
        
        print("[OK] Base de données réinitialisée")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la réinitialisation: {e}")
        return False

def remove_migrations():
    """Supprimer tous les fichiers de migration"""
    
    print("[INFO] Suppression des fichiers de migration...")
    
    apps = ['comptes', 'gestion_tenants', 'patients', 'medical', 
            'gestion_medicaments', 'rendez_vous', 'facturation', 'notifications']
    
    for app in apps:
        migrations_dir = f"{app}/migrations"
        if os.path.exists(migrations_dir):
            for file in os.listdir(migrations_dir):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(migrations_dir, file)
                    try:
                        os.remove(file_path)
                        print(f"[OK] Supprimé: {file_path}")
                    except Exception as e:
                        print(f"[ERROR] {file_path}: {e}")

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
    """Réinitialisation complète"""
    
    print("=" * 50)
    print("RÉINITIALISATION COMPLÈTE DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    # 1. Réinitialiser la base PostgreSQL
    if not reset_database():
        print("[ABORT] Impossible de réinitialiser la base")
        return False
    
    # 2. Supprimer les migrations
    remove_migrations()
    
    # 3. Recréer les migrations
    print("\n[INFO] Recréation des migrations...")
    apps = ['gestion_tenants', 'comptes', 'patients', 'medical', 
            'gestion_medicaments', 'rendez_vous', 'facturation', 'notifications']
    
    for app in apps:
        run_command(f"python manage.py makemigrations {app}", f"Migrations {app}")
    
    # 4. Appliquer les migrations
    run_command("python manage.py migrate", "Application des migrations")
    
    print("\n" + "=" * 50)
    print("RÉINITIALISATION TERMINÉE")
    print("=" * 50)
    print("\n[NEXT] Prochaines étapes:")
    print("1. python manage.py createsuperuser")
    print("2. python manage.py runserver 0.0.0.0:8000")
    
    return True

if __name__ == "__main__":
    if not os.path.exists('manage.py'):
        print("[ERROR] manage.py non trouvé")
        sys.exit(1)
    
    main()