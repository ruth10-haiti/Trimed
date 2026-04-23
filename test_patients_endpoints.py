#!/usr/bin/env python
"""
Script de test pour les endpoints patients
"""
import os
import sys
import django
import requests
import json
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion_tenants.models import Tenant
from patients.models import Patient

User = get_user_model()

# Configuration API
BASE_URL = 'http://localhost:8000/api'
HEADERS = {'Content-Type': 'application/json'}

def test_authentication():
    """Test de l'authentification"""
    print("🔐 Test d'authentification...")
    
    # Créer un utilisateur test si nécessaire
    try:
        user = User.objects.get(email='test@example.com')
    except User.DoesNotExist:
        # Créer un tenant test
        tenant, created = Tenant.objects.get_or_create(
            nom='Hôpital Test',
            defaults={
                'nombre_de_lits': 50,
                'statut': 'actif'
            }
        )
        
        # Créer un utilisateur test
        user = User.objects.creer_utilisateur(
            email='test@example.com',
            nom_complet='Docteur Test',
            mot_de_passe='testpass123',
            role='medecin',
            hopital=tenant
        )
        print("✅ Utilisateur test créé")
    
    # Test de login
    login_data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/comptes/login/', 
                               json=login_data, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            token = data['access']
            print("✅ Authentification réussie")
            return token
        else:
            print(f"❌ Échec authentification: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous qu'il est démarré.")
        return None

def test_patients_endpoints(token):
    """Test des endpoints patients"""
    if not token:
        print("❌ Pas de token, impossible de tester les endpoints")
        return
    
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n👥 Test des endpoints patients...")
    
    # Test GET /api/patients/
    try:
        response = requests.get(f'{BASE_URL}/patients/', headers=auth_headers)
        print(f"GET /api/patients/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Liste des patients récupérée ({len(data.get('results', []))} patients)")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors du test GET patients: {e}")
    
    # Test POST /api/patients/ (créer un patient)
    patient_data = {
        'nom': 'Dupont',
        'prenom': 'Jean',
        'date_naissance': '1980-01-01',
        'sexe': 'M',
        'numero_dossier_medical': f'TEST{date.today().strftime("%Y%m%d")}001',
        'telephone': '0123456789',
        'email': 'jean.dupont@test.com'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/patients/', 
                               json=patient_data, headers=auth_headers)
        print(f"POST /api/patients/ - Status: {response.status_code}")
        if response.status_code == 201:
            patient = response.json()
            patient_id = patient['patient_id']
            print(f"✅ Patient créé avec ID: {patient_id}")
            
            # Test GET /api/patients/{id}/
            response = requests.get(f'{BASE_URL}/patients/{patient_id}/', 
                                  headers=auth_headers)
            print(f"GET /api/patients/{patient_id}/ - Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Détail patient récupéré")
            
            # Test des endpoints spécialisés
            test_specialized_endpoints(token, patient_id)
            
        else:
            print(f"❌ Erreur création patient: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors du test POST patient: {e}")

def test_specialized_endpoints(token, patient_id):
    """Test des endpoints spécialisés pour un patient"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🏥 Test des endpoints spécialisés pour patient {patient_id}...")
    
    # Test statistiques patient
    try:
        response = requests.get(f'{BASE_URL}/patients/{patient_id}/statistiques/', 
                              headers=auth_headers)
        print(f"GET /api/patients/{patient_id}/statistiques/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Statistiques patient récupérées")
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")
    
    # Test ajout allergie
    allergie_data = {
        'nom_allergie': 'Pénicilline',
        'description': 'Allergie aux antibiotiques',
        'gravite': 'severe'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/patients/{patient_id}/ajouter_allergie/', 
                               json=allergie_data, headers=auth_headers)
        print(f"POST /api/patients/{patient_id}/ajouter_allergie/ - Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Allergie ajoutée")
    except Exception as e:
        print(f"❌ Erreur ajout allergie: {e}")
    
    # Test ajout antécédent
    antecedent_data = {
        'type_antecedent': 'maladie_chronique',
        'description': 'Diabète de type 2',
        'en_cours': True
    }
    
    try:
        response = requests.post(f'{BASE_URL}/patients/{patient_id}/ajouter_antecedent/', 
                               json=antecedent_data, headers=auth_headers)
        print(f"POST /api/patients/{patient_id}/ajouter_antecedent/ - Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Antécédent ajouté")
    except Exception as e:
        print(f"❌ Erreur ajout antécédent: {e}")

def test_related_endpoints(token):
    """Test des endpoints liés (adresses, contacts, etc.)"""
    if not token:
        return
    
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📋 Test des endpoints liés...")
    
    endpoints = [
        '/api/patients/adresses/',
        '/api/patients/contacts/',
        '/api/patients/assurances/',
        '/api/patients/allergies/',
        '/api/patients/antecedents/',
        '/api/patients/suivis/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL.replace("/api", "")}{endpoint}', 
                                  headers=auth_headers)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"GET {endpoint} - Status: {response.status_code} {status}")
        except Exception as e:
            print(f"❌ Erreur {endpoint}: {e}")

def main():
    print("🚀 Test des endpoints patients - Trimed Backend")
    print("=" * 50)
    
    # Test d'authentification
    token = test_authentication()
    
    if token:
        # Test des endpoints patients
        test_patients_endpoints(token)
        
        # Test des endpoints liés
        test_related_endpoints(token)
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés!")
    print("\n💡 Pour tester manuellement:")
    print("1. Démarrez le serveur: python manage.py runserver")
    print("2. Allez sur: http://localhost:8000/swagger/")
    print("3. Utilisez les credentials: test@example.com / testpass123")

if __name__ == '__main__':
    main()