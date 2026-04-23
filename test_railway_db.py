#!/usr/bin/env python
"""
Script pour tester la connexion à la base de données Railway
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def test_database_connection():
    """Tester la connexion à la base de données"""
    try:
        print("🔍 Test de connexion à la base de données...")
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connexion réussie! Version PostgreSQL: {version}")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def check_tables():
    """Vérifier les tables existantes"""
    try:
        print("\n📋 Vérification des tables...")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ {len(tables)} tables trouvées:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("⚠️ Aucune table trouvée - migrations nécessaires")
        return len(tables) > 0
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des tables: {e}")
        return False

def show_migration_status():
    """Afficher le statut des migrations"""
    try:
        print("\n🔄 Statut des migrations:")
        execute_from_command_line(['manage.py', 'showmigrations'])
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    print("🚀 Test de la base de données Railway\n")
    
    # Test de connexion
    if test_database_connection():
        # Vérifier les tables
        has_tables = check_tables()
        
        # Afficher le statut des migrations
        show_migration_status()
        
        if not has_tables:
            print("\n💡 Recommandation: Exécuter les migrations")
            print("   python manage.py migrate")
    
    print("\n🎉 Test terminé!")