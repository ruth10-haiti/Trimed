#!/usr/bin/env python
"""
Script de test pour vérifier que l'API fonctionne correctement
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Tester un endpoint de l'API"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🔍 Test: {description}")
    print(f"   {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"❌ Méthode {method} non supportée")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ Succès")
            return True
        else:
            print(f"   ❌ Erreur: {response.text[:100]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Impossible de se connecter au serveur")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

def main():
    """Tests principaux"""
    print("🧪 Tests de l'API Trimed Backend")
    print(f"   URL de base: {BASE_URL}")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health check
    total_tests += 1
    if test_endpoint("GET", "/health/", description="Health check"):
        tests_passed += 1
    
    # Test 2: API Info
    total_tests += 1
    if test_endpoint("GET", "/", description="API Info"):
        tests_passed += 1
    
    # Test 3: Swagger documentation
    total_tests += 1
    if test_endpoint("GET", "/swagger/", description="Documentation Swagger"):
        tests_passed += 1
    
    # Test 4: Login endpoint (sans données valides)
    total_tests += 1
    if test_endpoint("POST", "/api/comptes/login/", 
                    data={"email": "", "password": ""}, 
                    description="Endpoint de connexion (erreur attendue)"):
        # Ce test devrait échouer, donc on inverse le résultat
        pass
    else:
        tests_passed += 1  # L'erreur est attendue
    
    # Test 5: Liste des utilisateurs (sans authentification)
    total_tests += 1
    if test_endpoint("GET", "/api/comptes/utilisateurs/", 
                    description="Liste utilisateurs (erreur 401 attendue)"):
        # Ce test devrait échouer, donc on inverse le résultat
        pass
    else:
        tests_passed += 1  # L'erreur est attendue
    
    # Résultats
    print(f"\n📊 Résultats des tests:")
    print(f"   ✅ Tests réussis: {tests_passed}/{total_tests}")
    print(f"   📈 Taux de réussite: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print(f"\n🎉 Tous les tests sont passés! L'API est prête pour Flutter.")
        return True
    else:
        print(f"\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return False

def test_flutter_connectivity():
    """Tester la connectivité depuis Flutter (émulateur Android)"""
    print(f"\n📱 Test de connectivité Flutter (émulateur Android)")
    
    # Test avec l'IP de l'émulateur Android
    android_url = "http://10.0.2.2:8000"
    
    try:
        response = requests.get(f"{android_url}/health/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Connectivité émulateur Android OK")
            return True
        else:
            print(f"   ❌ Erreur émulateur Android: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Impossible de se connecter depuis l'émulateur Android")
        print(f"   💡 Assurez-vous que le serveur écoute sur 0.0.0.0:8000")
        return False

if __name__ == "__main__":
    success = main()
    test_flutter_connectivity()
    
    if success:
        print(f"\n🚀 L'API est prête! Vous pouvez maintenant:")
        print(f"   1. Connecter votre application Flutter")
        print(f"   2. Utiliser l'URL: http://10.0.2.2:8000 (émulateur Android)")
        print(f"   3. Consulter la documentation: {BASE_URL}/swagger/")
        sys.exit(0)
    else:
        print(f"\n🔧 Veuillez corriger les erreurs avant de continuer.")
        sys.exit(1)