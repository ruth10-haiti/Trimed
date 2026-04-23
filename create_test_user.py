#!/usr/bin/env python
"""
Créer un utilisateur de test simple
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_test_user():
    """Créer un utilisateur de test"""
    
    User = get_user_model()
    
    # Données de test
    email = "test@example.com"
    password = "password123"
    nom_complet = "Utilisateur Test"
    
    try:
        # Vérifier si l'utilisateur existe
        user = User.objects.get(email=email)
        print(f"[INFO] Utilisateur existant: {user.email}")
        
    except User.DoesNotExist:
        # Créer l'utilisateur
        user = User(
            email=email,
            nom_complet=nom_complet,
            role='patient',
            is_active=True
        )
        user.set_password(password)
        user.save()
        
        print(f"[OK] Utilisateur créé: {user.email}")
    
    # Créer un admin
    admin_email = "admin@example.com"
    admin_password = "admin123"
    
    try:
        admin = User.objects.get(email=admin_email)
        print(f"[INFO] Admin existant: {admin.email}")
        
    except User.DoesNotExist:
        admin = User(
            email=admin_email,
            nom_complet="Admin Test",
            role='admin-systeme',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        admin.set_password(admin_password)
        admin.save()
        
        print(f"[OK] Admin créé: {admin.email}")
    
    print(f"\n[SUCCESS] Données de test créées:")
    print(f"  Utilisateur: {email} / {password}")
    print(f"  Admin: {admin_email} / {admin_password}")
    print(f"  URL API: http://10.0.2.2:8000")

if __name__ == "__main__":
    create_test_user()