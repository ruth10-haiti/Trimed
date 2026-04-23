#!/usr/bin/env python
"""
Script de démarrage pour le développement
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Exécuter une commande avec gestion d'erreur"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Terminé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}:")
        print(f"   {e.stderr}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Démarrage du serveur de développement Trimed Backend")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('manage.py'):
        print("❌ Erreur: manage.py non trouvé. Assurez-vous d'être dans le répertoire du projet.")
        sys.exit(1)
    
    # Installer les dépendances
    if not run_command("pip install -r requirements.txt", "Installation des dépendances"):
        print("⚠️  Continuons malgré l'erreur d'installation...")
    
    # Migrations
    if not run_command("python manage.py makemigrations", "Création des migrations"):
        print("⚠️  Erreur lors de la création des migrations")
    
    if not run_command("python manage.py migrate", "Application des migrations"):
        print("❌ Erreur critique lors des migrations")
        sys.exit(1)
    
    # Collecter les fichiers statiques
    run_command("python manage.py collectstatic --noinput", "Collecte des fichiers statiques")
    
    # Créer un superutilisateur si nécessaire
    print("\n📝 Création d'un superutilisateur (optionnel)")
    print("   Appuyez sur Ctrl+C pour ignorer")
    try:
        subprocess.run("python manage.py createsuperuser", shell=True)
    except KeyboardInterrupt:
        print("\n⏭️  Création du superutilisateur ignorée")
    
    # Démarrer le serveur
    print("\n🌐 Démarrage du serveur sur http://127.0.0.1:8000")
    print("   API Documentation: http://127.0.0.1:8000/swagger/")
    print("   Admin: http://127.0.0.1:8000/admin/")
    print("   Appuyez sur Ctrl+C pour arrêter")
    
    try:
        subprocess.run("python manage.py runserver 0.0.0.0:8000", shell=True)
    except KeyboardInterrupt:
        print("\n👋 Serveur arrêté")

if __name__ == "__main__":
    main()