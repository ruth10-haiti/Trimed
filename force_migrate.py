#!/usr/bin/env python
"""
Script pour forcer les migrations sur Railway
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
    django.setup()
    
    print("🔄 Forçage des migrations...")
    
    # Lister les migrations en attente
    try:
        print("📋 Vérification des migrations en attente...")
        execute_from_command_line(['manage.py', 'showmigrations'])
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification: {e}")
    
    # Forcer les migrations
    try:
        print("🚀 Exécution forcée des migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Migrations forcées terminées")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        
    # Créer un superutilisateur si nécessaire
    try:
        print("👤 Création du superutilisateur...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(email='admin@trimed.com').exists():
            User.objects.create_superuser(
                email='admin@trimed.com',
                nom='Admin',
                prenom='System',
                password='admin123'
            )
            print("✅ Superutilisateur créé")
        else:
            print("ℹ️ Superutilisateur existe déjà")
    except Exception as e:
        print(f"⚠️ Erreur création superutilisateur: {e}")
    
    print("🎉 Script terminé!")