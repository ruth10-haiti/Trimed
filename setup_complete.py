#!/usr/bin/env python
"""
Configuration complète : Django + PostgreSQL + Données de test
"""
import os
import sys
import subprocess
import django

def run_command(command, description):
    """Exécuter une commande"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur:")
        print(f"   {e.stderr}")
        return False

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
    django.setup()

def create_migrations():
    """Créer et appliquer les migrations"""
    print("\n📦 Configuration de la base de données...")
    
    # Créer les migrations
    apps = ['gestion_tenants', 'comptes', 'patients', 'medical', 'gestion_medicaments', 'rendez_vous', 'facturation', 'notifications']
    
    for app in apps:
        run_command(f"python manage.py makemigrations {app}", f"Migrations {app}")
    
    # Appliquer les migrations
    run_command("python manage.py migrate", "Application des migrations")

def create_test_data():
    """Créer des données de test"""
    print("\n👤 Création des données de test...")
    
    from django.contrib.auth import get_user_model
    from gestion_tenants.models import Tenant
    
    User = get_user_model()
    
    # Créer un tenant simple
    try:
        tenant = Tenant.objects.create(
            nom="Hôpital de Test",
            adresse="123 Rue de Test",
            telephone="+33123456789",
            email_professionnel="test@hopital.com",
            directeur="Dr. Test",
            nombre_de_lits=50,
            statut='actif'
        )
        print(f"✅ Tenant créé: {tenant.nom}")
    except Exception as e:
        print(f"ℹ️  Tenant existe déjà ou erreur: {e}")
        tenant = None
    
    # Créer un utilisateur de test
    try:
        user = User.objects.create_user(
            email="test@example.com",
            nom_complet="Utilisateur Test",
            password="password123",
            role='patient',
            hopital=tenant
        )
        print(f"✅ Utilisateur créé: {user.email}")
    except Exception as e:
        print(f"ℹ️  Utilisateur existe déjà: {e}")
    
    # Créer un superutilisateur
    try:
        admin = User.objects.create_superuser(
            email="admin@example.com",
            nom_complet="Admin Test",
            password="admin123",
            role='admin-systeme'
        )
        print(f"✅ Admin créé: {admin.email}")
    except Exception as e:
        print(f"ℹ️  Admin existe déjà: {e}")

def main():
    """Configuration complète"""
    print("🚀 Configuration complète Trimed Backend + PostgreSQL")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('manage.py'):
        print("❌ Erreur: manage.py non trouvé")
        sys.exit(1)
    
    # Installer les dépendances
    run_command("pip install -r requirements.txt", "Installation des dépendances")
    
    # Configuration Django
    setup_django()
    
    # Migrations
    create_migrations()
    
    # Données de test
    create_test_data()
    
    print(f"\n🎉 Configuration terminée !")
    print(f"\n📱 Données de test pour Flutter:")
    print(f"   Email utilisateur: test@example.com")
    print(f"   Mot de passe: password123")
    print(f"   Email admin: admin@example.com")
    print(f"   Mot de passe admin: admin123")
    print(f"   URL API: http://10.0.2.2:8000")
    
    print(f"\n🌐 Pour démarrer le serveur:")
    print(f"   python manage.py runserver 0.0.0.0:8000")

if __name__ == "__main__":
    main()