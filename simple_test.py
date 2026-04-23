#!/usr/bin/env python
"""
Test simple pour Flutter - Créer un utilisateur de test
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_simple_user():
    """Créer un utilisateur simple pour les tests"""
    
    # Créer un utilisateur de test
    email = "test@example.com"
    password = "password123"
    
    try:
        user = User.objects.get(email=email)
        print(f"ℹ️  Utilisateur existant: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            nom_complet="Utilisateur Test",
            password=password,
            role='patient'
        )
        print(f"✅ Utilisateur créé: {user.email}")
    
    print(f"\n📱 Données de test pour Flutter:")
    print(f"   Email: {email}")
    print(f"   Mot de passe: {password}")
    print(f"   URL API: http://10.0.2.2:8000")
    print(f"\n🔗 Test de connexion:")
    print(f"   POST http://10.0.2.2:8000/api/comptes/login/")
    print(f"   Body: {{'email': '{email}', 'password': '{password}'}}")

if __name__ == "__main__":
    create_simple_user()