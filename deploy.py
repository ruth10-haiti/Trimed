#!/usr/bin/env python
"""
Script de déploiement pour Railway
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
    django.setup()
    
    print("🚀 Début du déploiement...")
    
    # Vérifier la connexion à la base de données
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Connexion à la base de données réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        sys.exit(1)
    
    # Exécuter les migrations
    try:
        print("📦 Exécution des migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations terminées")
    except Exception as e:
        print(f"❌ Erreur lors des migrations: {e}")
        sys.exit(1)
    
    # Collecter les fichiers statiques
    try:
        print("📁 Collection des fichiers statiques...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Fichiers statiques collectés")
    except Exception as e:
        print(f"❌ Erreur lors de la collection des fichiers statiques: {e}")
        sys.exit(1)
    
    print("🎉 Déploiement terminé avec succès!")