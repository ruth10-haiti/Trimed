# Guide de test de connexion Flutter ↔ Django

## Étape 1 : Démarrer le serveur Django

1. **Ouvrir un terminal dans le dossier backend** :
```bash
cd c:\Users\ruth\AndroidStudioProjects\trimed_hApp\trimed_h\trimed_backend
```

2. **Démarrer le serveur** :
```bash
python manage.py runserver 0.0.0.0:8000
```

3. **Vérifier que le serveur fonctionne** :
   - Ouvrir un navigateur
   - Aller à : http://127.0.0.1:8000/health/
   - Vous devriez voir : `{"status": "OK", "message": "Trimed Backend API is running", ...}`

## Étape 2 : Tester depuis Flutter

### Dans votre application Flutter :

1. **Ajouter les dépendances** dans `pubspec.yaml` :
```yaml
dependencies:
  http: ^1.1.0
  shared_preferences: ^2.2.2
```

2. **Créer un test simple** dans `lib/test_connection.dart` :
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ConnectionTest {
  static const String baseUrl = 'http://10.0.2.2:8000'; // Émulateur Android
  // static const String baseUrl = 'http://192.168.1.XXX:8000'; // Appareil physique
  
  static Future<void> testConnection() async {
    try {
      print('🔄 Test de connexion à $baseUrl...');
      
      // Test 1: Health check
      final healthResponse = await http.get(
        Uri.parse('$baseUrl/health/'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (healthResponse.statusCode == 200) {
        print('✅ Serveur accessible');
        print('   Réponse: ${healthResponse.body}');
      } else {
        print('❌ Erreur serveur: ${healthResponse.statusCode}');
      }
      
      // Test 2: Tentative de connexion (doit échouer sans utilisateur)
      final loginResponse = await http.post(
        Uri.parse('$baseUrl/api/comptes/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': 'test@example.com',
          'password': 'wrongpassword',
        }),
      );
      
      if (loginResponse.statusCode == 400) {
        print('✅ Endpoint de connexion accessible');
        print('   Erreur attendue: ${loginResponse.body}');
      } else {
        print('⚠️  Réponse inattendue: ${loginResponse.statusCode}');
      }
      
    } catch (e) {
      print('❌ Erreur de connexion: $e');
      print('💡 Vérifiez que :');
      print('   - Le serveur Django est démarré');
      print('   - L\'URL est correcte');
      print('   - Vous êtes sur le même réseau');
    }
  }
}
```

3. **Appeler le test** dans votre `main.dart` :
```dart
import 'package:flutter/material.dart';
import 'test_connection.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: TestScreen(),
    );
  }
}

class TestScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Test Connexion')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            ConnectionTest.testConnection();
          },
          child: Text('Tester la connexion'),
        ),
      ),
    );
  }
}
```

## Étape 3 : Vérifier les résultats

### Résultats attendus :

1. **✅ Serveur accessible** - Le health check fonctionne
2. **✅ Endpoint de connexion accessible** - L'API répond (même avec une erreur)

### Si ça ne marche pas :

1. **Vérifier l'URL** :
   - Émulateur Android : `http://10.0.2.2:8000`
   - Appareil physique : `http://[IP_DE_VOTRE_PC]:8000`

2. **Trouver l'IP de votre PC** :
```bash
ipconfig
```
Cherchez l'adresse IPv4 de votre carte réseau.

3. **Vérifier le firewall** :
   - Autoriser Python/Django dans le firewall Windows

## Étape 4 : Test avec Postman (optionnel)

1. **Installer Postman**
2. **Tester** :
   - GET `http://127.0.0.1:8000/health/`
   - POST `http://127.0.0.1:8000/api/comptes/login/`
     ```json
     {
       "email": "test@example.com",
       "password": "test123"
     }
     ```

## Résultats attendus

- ✅ **Health check** : Status 200, message "API is running"
- ✅ **Login endpoint** : Status 400, erreur de validation (normal sans utilisateur)
- ❌ **Pas de réponse** : Problème de réseau ou serveur arrêté

Une fois ces tests réussis, votre connexion Flutter ↔ Django fonctionne !