#!/usr/bin/env python
"""
Script de test pour les endpoints gestion des médicaments
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
from gestion_medicaments.models import Medicament, MedicamentCategorie

User = get_user_model()

# Configuration API
BASE_URL = 'http://localhost:8000/api'
HEADERS = {'Content-Type': 'application/json'}

def setup_medicament_test_data():
    """Créer les données de test pour les médicaments"""
    print("💊 Configuration des données de test médicaments...")
    
    # Créer un tenant test
    tenant, created = Tenant.objects.get_or_create(
        nom='Pharmacie Test',
        defaults={
            'nombre_de_lits': 30,
            'statut': 'actif'
        }
    )
    
    # Créer un utilisateur pharmacien
    try:
        pharmacien_user = User.objects.get(email='pharmacien@test.com')
    except User.DoesNotExist:
        pharmacien_user = User.objects.creer_utilisateur(
            email='pharmacien@test.com',
            nom_complet='Marie Pharmacien',
            mot_de_passe='testpass123',
            role='personnel',
            hopital=tenant
        )
    
    # Créer des catégories de médicaments
    categories_data = [
        {'nom': 'Antalgiques', 'description': 'Médicaments contre la douleur'},
        {'nom': 'Antibiotiques', 'description': 'Médicaments contre les infections'},
        {'nom': 'Cardiovasculaires', 'description': 'Médicaments pour le cœur'},
        {'nom': 'Vitamines', 'description': 'Compléments vitaminiques'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        cat, created = MedicamentCategorie.objects.get_or_create(
            tenant=tenant,
            nom=cat_data['nom'],
            defaults={'description': cat_data['description']}
        )
        categories[cat_data['nom']] = cat
    
    # Créer des médicaments de test
    medicaments_data = [
        {
            'nom': 'Paracétamol 500mg',
            'forme_pharmaceutique': 'comprime',
            'dosage_standard': '500mg',
            'categorie': categories['Antalgiques'],
            'stock_actuel': 150,
            'stock_minimum': 50,
            'prix_unitaire': 0.25,
            'necessite_ordonnance': False,
            'dci': 'Paracétamol'
        },
        {
            'nom': 'Amoxicilline 1g',
            'forme_pharmaceutique': 'comprime',
            'dosage_standard': '1g',
            'categorie': categories['Antibiotiques'],
            'stock_actuel': 5,  # Stock faible
            'stock_minimum': 20,
            'prix_unitaire': 1.50,
            'necessite_ordonnance': True,
            'dci': 'Amoxicilline'
        },
        {
            'nom': 'Aspirine 100mg',
            'forme_pharmaceutique': 'comprime',
            'dosage_standard': '100mg',
            'categorie': categories['Cardiovasculaires'],
            'stock_actuel': 0,  # Rupture de stock
            'stock_minimum': 30,
            'prix_unitaire': 0.15,
            'necessite_ordonnance': False,
            'dci': 'Acide acétylsalicylique'
        },
        {
            'nom': 'Vitamine D3 1000UI',
            'forme_pharmaceutique': 'capsule',
            'dosage_standard': '1000UI',
            'categorie': categories['Vitamines'],
            'stock_actuel': 200,
            'stock_minimum': 25,
            'prix_unitaire': 0.80,
            'necessite_ordonnance': False,
            'dci': 'Cholécalciférol'
        }
    ]
    
    medicaments = []
    for med_data in medicaments_data:
        med, created = Medicament.objects.get_or_create(
            tenant=tenant,
            nom=med_data['nom'],
            defaults=med_data
        )
        medicaments.append(med)
    
    print("✅ Données de test médicaments créées")
    return {
        'tenant': tenant,
        'pharmacien_user': pharmacien_user,
        'categories': categories,
        'medicaments': medicaments
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

def test_medicament_endpoints(token, test_data):
    """Test des endpoints médicaments"""
    if not token:
        print("❌ Pas de token, impossible de tester")
        return
    
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n💊 Test des endpoints médicaments...")
    
    # Test GET médicaments
    try:
        response = requests.get(f'{BASE_URL}/medicaments/', headers=auth_headers)
        print(f"GET /api/medicaments/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Médicaments récupérés ({len(data.get('results', []))} médicaments)")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur GET médicaments: {e}")
    
    # Test POST médicament (créer un nouveau médicament)
    nouveau_medicament = {
        'nom': 'Ibuprofène 400mg',
        'forme_pharmaceutique': 'comprime',
        'dosage_standard': '400mg',
        'categorie': test_data['categories']['Antalgiques'].categorie_id,
        'stock_actuel': 100,
        'stock_minimum': 30,
        'prix_unitaire': 0.35,
        'necessite_ordonnance': False,
        'dci': 'Ibuprofène',
        'description': 'Anti-inflammatoire non stéroïdien'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/medicaments/', 
                               json=nouveau_medicament, headers=auth_headers)
        print(f"POST /api/medicaments/ - Status: {response.status_code}")
        if response.status_code == 201:
            medicament = response.json()
            medicament_id = medicament['medicament_id']
            print(f"✅ Médicament créé avec ID: {medicament_id}")
            
            # Test des actions sur le médicament
            test_medicament_actions(token, medicament_id)
            
        else:
            print(f"❌ Erreur création médicament: {response.text}")
    except Exception as e:
        print(f"❌ Erreur POST médicament: {e}")

def test_medicament_actions(token, medicament_id):
    """Test des actions sur un médicament"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n📦 Test des actions sur médicament {medicament_id}...")
    
    # Test mise à jour du stock (entrée)
    stock_update_data = {
        'type_mouvement': 'entree',
        'quantite': 50,
        'motif': 'Réapprovisionnement',
        'prix_unitaire': 0.30
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/medicaments/{medicament_id}/mettre_a_jour_stock/',
            json=stock_update_data, headers=auth_headers
        )
        print(f"POST /api/medicaments/{medicament_id}/mettre_a_jour_stock/ - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Stock mis à jour: {result['ancien_stock']} → {result['nouveau_stock']}")
        else:
            print(f"❌ Erreur mise à jour stock: {response.text}")
    except Exception as e:
        print(f"❌ Erreur stock: {e}")
    
    # Test mise à jour du stock (sortie)
    stock_sortie_data = {
        'type_mouvement': 'sortie',
        'quantite': 25,
        'motif': 'Dispensation patient'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/medicaments/{medicament_id}/mettre_a_jour_stock/',
            json=stock_sortie_data, headers=auth_headers
        )
        print(f"POST sortie stock - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sortie stock: {result['ancien_stock']} → {result['nouveau_stock']}")
    except Exception as e:
        print(f"❌ Erreur sortie stock: {e}")

def test_stock_endpoints(token):
    """Test des endpoints de gestion du stock"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Test des endpoints de stock...")
    
    endpoints = [
        '/api/medicaments/stock_faible/',
        '/api/medicaments/rupture_stock/',
        '/api/medicaments/statistiques/',
        '/api/medicaments/export_stock/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL.replace("/api", "")}{endpoint}', 
                                  headers=auth_headers)
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"GET {endpoint} - Status: {response.status_code} {status_icon}")
            
            if response.status_code == 200 and 'statistiques' in endpoint:
                stats = response.json()
                print(f"   📈 {stats.get('total_medicaments', 0)} médicaments total")
                print(f"   ⚠️ {stats.get('medicaments_rupture', 0)} en rupture")
                print(f"   💰 {stats.get('valeur_stock_total', 0)}€ valeur stock")
                
        except Exception as e:
            print(f"❌ Erreur {endpoint}: {e}")

def test_categories_endpoints(token):
    """Test des endpoints catégories"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📂 Test des catégories...")
    
    # Test GET catégories
    try:
        response = requests.get(f'{BASE_URL}/medicaments/categories/', headers=auth_headers)
        print(f"GET /api/medicaments/categories/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Catégories récupérées ({len(data.get('results', data))} catégories)")
    except Exception as e:
        print(f"❌ Erreur catégories: {e}")
    
    # Test POST nouvelle catégorie
    nouvelle_categorie = {
        'nom': 'Dermatologie',
        'description': 'Médicaments pour la peau'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/medicaments/categories/', 
                               json=nouvelle_categorie, headers=auth_headers)
        print(f"POST /api/medicaments/categories/ - Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Catégorie créée")
    except Exception as e:
        print(f"❌ Erreur création catégorie: {e}")

def test_recherche_avancee(token):
    """Test de la recherche avancée"""
    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n🔍 Test de la recherche avancée...")
    
    # Recherche par nom
    recherche_data = {
        'nom': 'paracetamol',
        'necessite_ordonnance': False,
        'prix_max': 1.00
    }
    
    try:
        response = requests.post(f'{BASE_URL}/medicaments/recherche_avancee/', 
                               json=recherche_data, headers=auth_headers)
        print(f"POST /api/medicaments/recherche_avancee/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recherche: {len(data.get('results', data))} résultats")
    except Exception as e:
        print(f"❌ Erreur recherche: {e}")

def main():
    print("🚀 Test des endpoints gestion médicaments - Trimed Backend")
    print("=" * 70)
    
    # Configuration des données de test
    test_data = setup_medicament_test_data()
    
    # Test avec utilisateur pharmacien
    print("\n🔐 Test avec utilisateur pharmacien...")
    token = get_auth_token('pharmacien@test.com', 'testpass123')
    
    if token:
        test_medicament_endpoints(token, test_data)
        test_stock_endpoints(token)
        test_categories_endpoints(token)
        test_recherche_avancee(token)
    
    print("\n" + "=" * 70)
    print("✅ Tests terminés!")
    print("\n💡 Pour tester manuellement:")
    print("1. Démarrez le serveur: python manage.py runserver")
    print("2. Allez sur: http://localhost:8000/swagger/")
    print("3. Utilisez les credentials:")
    print("   - Pharmacien: pharmacien@test.com / testpass123")
    print("\n📚 Endpoints disponibles:")
    print("   - GET/POST /api/medicaments/")
    print("   - POST /api/medicaments/{id}/mettre_a_jour_stock/")
    print("   - GET /api/medicaments/stock_faible/")
    print("   - GET /api/medicaments/rupture_stock/")
    print("   - GET /api/medicaments/statistiques/")
    print("   - GET/POST /api/medicaments/categories/")

if __name__ == '__main__':
    main()