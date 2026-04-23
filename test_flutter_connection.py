#!/usr/bin/env python
"""
Test de connexion Flutter - Créer un utilisateur de test
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
django.setup()

from comptes.models import Utilisateur
from gestion_tenants.models import Tenant

def create_test_data():
    """Créer des données de test pour Flutter"""
    
    # Créer un tenant de test
    tenant, created = Tenant.objects.get_or_create(
        nom="Hôpital de Test",
        defaults={
            'adresse': '123 Rue de Test',
            'telephone': '+33123456789',
            'email_professionnel': 'test@hopital.com',
            'directeur': 'Dr. Test',
            'nombre_de_lits': 50,
            'statut': 'actif'
        }
    )
    
    if created:
        print(f"✅ Tenant créé: {tenant.nom}")
    else:
        print(f"ℹ️  Tenant existant: {tenant.nom}")
    
    # Créer un utilisateur de test
    user, created = Utilisateur.objects.get_or_create(
        email="test@example.com",
        defaults={
            'nom_complet': 'Utilisateur Test',
            'role': 'patient',
            'hopital': tenant,
            'is_active': True
        }
    )
    
    if created:
        user.set_password('password123')
        user.save()
        print(f"✅ Utilisateur créé: {user.email}")
    else:
        print(f"ℹ️  Utilisateur existant: {user.email}")
    
    print(f"\n📱 Données de test pour Flutter:")
    print(f"   Email: test@example.com")
    print(f"   Mot de passe: password123")
    print(f"   URL API: http://10.0.2.2:8000")

if __name__ == "__main__":
    create_test_data()