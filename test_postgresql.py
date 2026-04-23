#!/usr/bin/env python
"""
Test de connexion PostgreSQL
"""
import psycopg2
from psycopg2 import sql

def test_postgresql_connection():
    """Tester la connexion à PostgreSQL"""
    
    # Paramètres de connexion
    config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'Trimedh_BD',
        'user': 'admin_Trimedh',
        'password': 'root'
    }
    
    try:
        print("[INFO] Test de connexion PostgreSQL...")
        
        # Connexion à PostgreSQL
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Test simple
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("[OK] Connexion PostgreSQL reussie")
        print(f"   Version: {version[0][:50]}...")
        
        # Vérifier la base de données
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"   Base de donnees: {db_name}")
        
        # Fermer la connexion
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"[ERROR] Erreur PostgreSQL: {e}")
        print("\n[HELP] Solutions possibles:")
        print("   1. Verifier que PostgreSQL est demarre")
        print("   2. Creer la base de donnees 'Trimedh_BD'")
        print("   3. Creer l'utilisateur 'admin_Trimedh' avec le mot de passe 'root'")
        print("   4. Verifier les parametres de connexion")
        return False
    
    except Exception as e:
        print(f"[ERROR] Erreur generale: {e}")
        return False

if __name__ == "__main__":
    if test_postgresql_connection():
        print("\n[SUCCESS] PostgreSQL est pret pour Django !")
        print("\n[NEXT] Prochaines etapes:")
        print("   1. python setup_complete.py")
        print("   2. python manage.py runserver 0.0.0.0:8000")
    else:
        print("\n[TODO] Configurez PostgreSQL avant de continuer")