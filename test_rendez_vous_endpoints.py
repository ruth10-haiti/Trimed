#!/usr/bin/env python
"""
Script de test pour les endpoints rendez-vous
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion_tenants.models import Tenant
from patients.models import Patient
from medical.models import Medecin, Specialite
from rendez_vous.models import RendezVous, RendezVousType, RendezVousStatut

User = get_user_model()

# Configuration API
BASE_URL = 'http://localhost:8000/api'
HEADERS = {'Content-Type': 'application/json'}

def setup_test_data():
    """Créer les données de test nécessaires"""
    print("🔧 Configuration des données de test...")
    
    # Créer un tenant test
    tenant, created = Tenant.objects.get_or_create(
        nom='Hôpital Test RDV',
        defaults={
            'nombre_de_lits': 100,
            'statut': 'actif'
        }
    )
    
    # Créer un utilisateur médecin
    try:
        medecin_user = User.objects.get(email='medecin@test.com')
    except User.DoesNotExist:
        medecin_user = User.objects.creer_utilisateur(
            email='medecin@test.com',
            nom_complet='Dr. Martin Dupont',
            mot_de_passe='testpass123',
            role='medecin',
            hopital=tenant
        )
    
    # Créer un utilisateur secrétaire
    try:
        secretaire_user = User.objects.get(email='secretaire@test.com')
    except User.DoesNotExist:
        secretaire_user = User.objects.creer_utilisateur(
            email='secretaire@test.com',
            nom_complet='Marie Secrétaire',
            mot_de_passe='testpass123',
            role='secretaire',
            hopital=tenant
        )
    
    # Créer une spécialité
    specialite, created = Specialite.objects.get_or_create(
        nom_specialite='Médecine Générale',
        defaults={'description': 'Consultation générale'}
    )
    
    # Créer un médecin
    medecin, created = Medecin.objects.get_or_create(
        email_professionnel='medecin@test.com',
        defaults={
            'hopital': tenant,
            'nom': 'Dupont',
            'prenom': 'Martin',
            'specialite_principale': specialite,
            'utilisateur': medecin_user
        }
    )
    
    # Créer un patient
    patient, created = Patient.objects.get_or_create(
        numero_dossier_medical='RDV001',
        defaults={
            'hopital': tenant,
            'nom': 'Patient',
            'prenom': 'Test',
            'telephone': '0123456789',
            'email': 'patient@test.com'
        }
    )
    
    # Créer des types de RDV
    type_consultation, created = RendezVousType.objects.get_or_create(
        tenant=tenant,
        nom='Consultation',
        defaults={
            'description': 'Consultation médicale standard',
            'duree_defaut': 30,
            'couleur': '#3498db'
        }
    )
    
    type_urgence, created = RendezVousType.objects.get_or_create(
        tenant=tenant,
        nom='Urgence',
        defaults={
            'description': 'Consultation d\'urgence',
            'duree_defaut': 45,
            'couleur': '#e74c3c'
        }
    )
    
    # Créer des statuts
    statut_planifie, created = RendezVousStatut.objects.get_or_create(
        tenant=tenant,
        nom='Planifié',
        defaults={
            'description': 'Rendez-vous planifié',
            'couleur': '#3498db',
            'est_confirme': False
        }
    )
    
    print("✅ Données de test créées")
    return {
        'tenant': tenant,
        'medecin_user': medecin_user,
        'secretaire_user': secretaire_user,
        'medecin': medecin,
        'patient': patient,
        'type_consultation': type_consultation,
        'statut_planifie': statut_planifie
    }

def get_auth_token(email, password):
    """Obtenir un token d'authentification"""
    login_data = {
        'email': email,
        'password': password
    }
    
    try:
        response = requests.post(f'{BASE_URL}/comptes/login/', 
                               json=login_data, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data['access']
        else:
            print(f"❌ Échec authentification: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        return None

def test_rendez_vous_endpoints(token, test_data):
    """Test des endpoints rendez-vous"""
    if not token:
        print("❌ Pas de token, impossible de tester")
        return
    
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📅 Test des endpoints rendez-vous...")
    
    # Test GET /api/rendez-vous/
    try:
        response = requests.get(f'{BASE_URL}/rendez-vous/', headers=auth_headers)
        print(f"GET /api/rendez-vous/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Liste des RDV récupérée ({len(data.get('results', []))} RDV)")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors du test GET RDV: {e}")
    
    # Test POST /api/rendez-vous/ (créer un RDV)
    demain = datetime.now() + timedelta(days=1)
    rdv_data = {
        'patient': test_data['patient'].patient_id,
        'medecin': test_data['medecin'].medecin_id,
        'date_heure': demain.replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
        'type': test_data['type_consultation'].type_id,
        'motif': 'Consultation de contrôle',
        'notes': 'Patient en bonne santé générale'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/rendez-vous/', 
                               json=rdv_data, headers=auth_headers)
        print(f"POST /api/rendez-vous/ - Status: {response.status_code}")
        if response.status_code == 201:
            rdv = response.json()
            rdv_id = rdv['rendez_vous_id']
            print(f"✅ RDV créé avec ID: {rdv_id}")
            
            # Test des actions spécialisées
            test_rdv_actions(token, rdv_id, test_data)
            
        else:
            print(f"❌ Erreur création RDV: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors du test POST RDV: {e}")

def test_rdv_actions(token, rdv_id, test_data):
    """Test des actions spécialisées sur un RDV"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🎯 Test des actions spécialisées pour RDV {rdv_id}...")
    
    # Test confirmer RDV
    try:
        response = requests.post(f'{BASE_URL}/rendez-vous/{rdv_id}/confirmer/', 
                               headers=auth_headers)
        print(f"POST /api/rendez-vous/{rdv_id}/confirmer/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ RDV confirmé")
    except Exception as e:
        print(f"❌ Erreur confirmation: {e}")
    
    # Test reporter RDV
    nouvelle_date = (datetime.now() + timedelta(days=2)).replace(
        hour=14, minute=0, second=0, microsecond=0
    ).isoformat()
    
    try:
        response = requests.post(f'{BASE_URL}/rendez-vous/{rdv_id}/reporter/', 
                               json={'nouvelle_date_heure': nouvelle_date},
                               headers=auth_headers)
        print(f"POST /api/rendez-vous/{rdv_id}/reporter/ - Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ RDV reporté")
    except Exception as e:
        print(f"❌ Erreur report: {e}")

def test_creneaux_disponibles(token, test_data):
    """Test des créneaux disponibles"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n🕐 Test des créneaux disponibles...")
    
    demain = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        response = requests.get(
            f'{BASE_URL}/rendez-vous/creneaux_disponibles/',
            params={
                'medecin_id': test_data['medecin'].medecin_id,
                'date': demain,
                'duree': 30
            },
            headers=auth_headers
        )
        print(f"GET /api/rendez-vous/creneaux_disponibles/ - Status: {response.status_code}")
        if response.status_code == 200:
            creneaux = response.json()
            disponibles = [c for c in creneaux if c['disponible']]
            print(f"✅ {len(disponibles)} créneaux disponibles sur {len(creneaux)}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur créneaux: {e}")

def test_types_et_statuts(token):
    """Test des endpoints types et statuts"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📋 Test des types et statuts...")
    
    endpoints = [
        '/api/rendez-vous/types/',
        '/api/rendez-vous/statuts/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL.replace("/api", "")}{endpoint}', 
                                  headers=auth_headers)
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"GET {endpoint} - Status: {response.status_code} {status_icon}")
        except Exception as e:
            print(f"❌ Erreur {endpoint}: {e}")

def test_statistiques(token):
    """Test des statistiques"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Test des statistiques...")
    
    try:
        response = requests.get(f'{BASE_URL}/rendez-vous/statistiques/', 
                              headers=auth_headers)
        print(f"GET /api/rendez-vous/statistiques/ - Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistiques: {stats['total']} RDV total")
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")

def main():
    print("🚀 Test des endpoints rendez-vous - Trimed Backend")
    print("=" * 60)
    
    # Configuration des données de test
    test_data = setup_test_data()
    
    # Test avec utilisateur secrétaire (peut créer des RDV)
    print("\n🔐 Test avec utilisateur secrétaire...")
    token = get_auth_token('secretaire@test.com', 'testpass123')
    
    if token:
        test_rendez_vous_endpoints(token, test_data)
        test_creneaux_disponibles(token, test_data)
        test_types_et_statuts(token)
        test_statistiques(token)
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés!")
    print("\n💡 Pour tester manuellement:")
    print("1. Démarrez le serveur: python manage.py runserver")
    print("2. Allez sur: http://localhost:8000/swagger/")
    print("3. Utilisez les credentials:")
    print("   - Secrétaire: secretaire@test.com / testpass123")
    print("   - Médecin: medecin@test.com / testpass123")

if __name__ == '__main__':
    main()