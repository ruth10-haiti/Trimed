#!/usr/bin/env python
"""
Script de test pour les endpoints consultations médicales
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
from medical.models import Medecin, Specialite, Consultation, Ordonnance
from rendez_vous.models import RendezVous, RendezVousType, RendezVousStatut

User = get_user_model()

# Configuration API
BASE_URL = 'http://localhost:8000/api'
HEADERS = {'Content-Type': 'application/json'}

def setup_medical_test_data():
    """Créer les données de test pour le module médical"""
    print("🏥 Configuration des données de test médicales...")
    
    # Créer un tenant test
    tenant, created = Tenant.objects.get_or_create(
        nom='Clinique Médicale Test',
        defaults={
            'nombre_de_lits': 50,
            'statut': 'actif'
        }
    )
    
    # Créer un utilisateur médecin
    try:
        medecin_user = User.objects.get(email='dr.martin@test.com')
    except User.DoesNotExist:
        medecin_user = User.objects.creer_utilisateur(
            email='dr.martin@test.com',
            nom_complet='Dr. Martin Leblanc',
            mot_de_passe='testpass123',
            role='medecin',
            hopital=tenant
        )
    
    # Créer une spécialité
    specialite, created = Specialite.objects.get_or_create(
        nom_specialite='Cardiologie',
        defaults={'description': 'Spécialité du cœur et des vaisseaux'}
    )
    
    # Créer un médecin
    medecin, created = Medecin.objects.get_or_create(
        email_professionnel='dr.martin@test.com',
        defaults={
            'hopital': tenant,
            'nom': 'Leblanc',
            'prenom': 'Martin',
            'specialite_principale': specialite,
            'telephone': '0123456789',
            'utilisateur': medecin_user
        }
    )
    
    # Créer un patient
    patient, created = Patient.objects.get_or_create(
        numero_dossier_medical='MED001',
        defaults={
            'hopital': tenant,
            'nom': 'Dupont',
            'prenom': 'Jean',
            'date_naissance': '1975-05-15',
            'sexe': 'M',
            'telephone': '0987654321',
            'email': 'jean.dupont@test.com'
        }
    )
    
    # Créer un type de RDV
    rdv_type, created = RendezVousType.objects.get_or_create(
        tenant=tenant,
        nom='Consultation Cardiologie',
        defaults={
            'description': 'Consultation spécialisée en cardiologie',
            'duree_defaut': 45,
            'couleur': '#e74c3c'
        }
    )
    
    # Créer un statut RDV
    rdv_statut, created = RendezVousStatut.objects.get_or_create(
        tenant=tenant,
        nom='Terminé',
        defaults={
            'description': 'Rendez-vous terminé',
            'couleur': '#2ecc71',
            'est_termine': True
        }
    )
    
    # Créer un RDV passé pour la consultation
    rdv, created = RendezVous.objects.get_or_create(
        patient=patient,
        medecin=medecin,
        defaults={
            'tenant': tenant,
            'date_heure': datetime.now() - timedelta(hours=2),
            'type': rdv_type,
            'statut': rdv_statut,
            'motif': 'Consultation de contrôle cardiaque'
        }
    )
    
    print("✅ Données de test médicales créées")
    return {
        'tenant': tenant,
        'medecin_user': medecin_user,
        'medecin': medecin,
        'patient': patient,
        'specialite': specialite,
        'rdv': rdv
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

def test_medical_endpoints(token, test_data):
    """Test des endpoints médicaux"""
    if not token:
        print("❌ Pas de token, impossible de tester")
        return
    
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n🏥 Test des endpoints médicaux...")
    
    # Test des spécialités
    try:
        response = requests.get(f'{BASE_URL}/medical/specialites/', headers=auth_headers)
        print(f"GET /api/medical/specialites/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Spécialités récupérées ({len(data.get('results', data))} spécialités)")
    except Exception as e:
        print(f"❌ Erreur spécialités: {e}")
    
    # Test des médecins
    try:
        response = requests.get(f'{BASE_URL}/medical/medecins/', headers=auth_headers)
        print(f"GET /api/medical/medecins/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Médecins récupérés ({len(data.get('results', []))} médecins)")
    except Exception as e:
        print(f"❌ Erreur médecins: {e}")

def test_consultation_endpoints(token, test_data):
    """Test des endpoints consultations"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n👩‍⚕️ Test des consultations...")
    
    # Test GET consultations
    try:
        response = requests.get(f'{BASE_URL}/medical/consultations/', headers=auth_headers)
        print(f"GET /api/medical/consultations/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Consultations récupérées ({len(data.get('results', []))} consultations)")
    except Exception as e:
        print(f"❌ Erreur GET consultations: {e}")
    
    # Test POST consultation (créer une consultation)
    consultation_data = {
        'patient': test_data['patient'].patient_id,
        'medecin': test_data['medecin'].medecin_id,
        'rendez_vous': test_data['rdv'].rendez_vous_id,
        'date_consultation': datetime.now().isoformat(),
        'motif': 'Consultation de contrôle cardiaque',
        'diagnostic_principal': 'Tension artérielle légèrement élevée',
        'notes': 'Patient en bonne santé générale. Recommandation de surveillance.'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/medical/consultations/', 
                               json=consultation_data, headers=auth_headers)
        print(f"POST /api/medical/consultations/ - Status: {response.status_code}")
        if response.status_code == 201:
            consultation = response.json()
            consultation_id = consultation['consultation_id']
            print(f"✅ Consultation créée avec ID: {consultation_id}")
            
            # Test des actions sur la consultation
            test_consultation_actions(token, consultation_id, test_data)
            
        else:
            print(f"❌ Erreur création consultation: {response.text}")
    except Exception as e:
        print(f"❌ Erreur POST consultation: {e}")

def test_consultation_actions(token, consultation_id, test_data):
    """Test des actions sur une consultation"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n💊 Test des actions sur consultation {consultation_id}...")
    
    # Test créer ordonnance
    ordonnance_data = {
        'date_ordonnance': datetime.now().isoformat(),
        'recommandations': 'Prendre les médicaments selon prescription. Contrôle dans 1 mois.',
        'prescriptions': [
            {
                'medicament': 1,  # Supposons qu'il existe
                'dosage': '5mg',
                'frequence': '1 fois par jour',
                'duree': '30 jours',
                'quantite': 30,
                'instructions': 'À prendre le matin avec un verre d\'eau'
            }
        ]
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/medical/consultations/{consultation_id}/creer_ordonnance/',
            json=ordonnance_data, headers=auth_headers
        )
        print(f"POST /api/medical/consultations/{consultation_id}/creer_ordonnance/ - Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Ordonnance créée")
        else:
            print(f"⚠️ Ordonnance non créée: {response.text}")
    except Exception as e:
        print(f"❌ Erreur ordonnance: {e}")
    
    # Test prescrire examen
    examen_data = {
        'nom_examen': 'Électrocardiogramme (ECG)',
        'type_examen': 'ecg',
        'date_examen': (datetime.now() + timedelta(days=7)).isoformat(),
        'notes': 'ECG de contrôle pour vérifier le rythme cardiaque'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/medical/consultations/{consultation_id}/prescrire_examen/',
            json=examen_data, headers=auth_headers
        )
        print(f"POST /api/medical/consultations/{consultation_id}/prescrire_examen/ - Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Examen prescrit")
        else:
            print(f"⚠️ Examen non prescrit: {response.text}")
    except Exception as e:
        print(f"❌ Erreur examen: {e}")

def test_ordonnances_examens(token):
    """Test des endpoints ordonnances et examens"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📋 Test des ordonnances et examens...")
    
    endpoints = [
        '/api/medical/ordonnances/',
        '/api/medical/examens/',
        '/api/medical/prescriptions/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL.replace("/api", "")}{endpoint}', 
                                  headers=auth_headers)
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"GET {endpoint} - Status: {response.status_code} {status_icon}")
        except Exception as e:
            print(f"❌ Erreur {endpoint}: {e}")

def test_medecin_statistiques(token, test_data):
    """Test des statistiques médecin"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Test des statistiques médecin...")
    
    try:
        response = requests.get(
            f'{BASE_URL}/medical/medecins/{test_data["medecin"].medecin_id}/statistiques/',
            headers=auth_headers
        )
        print(f"GET /api/medical/medecins/{test_data['medecin'].medecin_id}/statistiques/ - Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistiques: {stats.get('consultations_total', 0)} consultations")
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")

def main():
    print("🚀 Test des endpoints consultations médicales - Trimed Backend")
    print("=" * 70)
    
    # Configuration des données de test
    test_data = setup_medical_test_data()
    
    # Test avec utilisateur médecin
    print("\n🔐 Test avec utilisateur médecin...")
    token = get_auth_token('dr.martin@test.com', 'testpass123')
    
    if token:
        test_medical_endpoints(token, test_data)
        test_consultation_endpoints(token, test_data)
        test_ordonnances_examens(token)
        test_medecin_statistiques(token, test_data)
    
    print("\n" + "=" * 70)
    print("✅ Tests terminés!")
    print("\n💡 Pour tester manuellement:")
    print("1. Démarrez le serveur: python manage.py runserver")
    print("2. Allez sur: http://localhost:8000/swagger/")
    print("3. Utilisez les credentials:")
    print("   - Médecin: dr.martin@test.com / testpass123")
    print("\n📚 Endpoints disponibles:")
    print("   - GET/POST /api/medical/consultations/")
    print("   - GET/POST /api/medical/ordonnances/")
    print("   - GET/POST /api/medical/examens/")
    print("   - GET /api/medical/medecins/")
    print("   - GET /api/medical/specialites/")

if __name__ == '__main__':
    main()