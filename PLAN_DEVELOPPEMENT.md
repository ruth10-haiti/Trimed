# Plan de Développement - Application Trimed

## 🎯 Objectif
Créer une application complète de gestion hospitalière avec Django (Backend) + Flutter (Frontend)

## 📋 Étapes de Développement

### Phase 1 : Backend API (Django) ✅ TERMINÉ
- [x] Configuration PostgreSQL
- [x] Modèles de données (Patients, Médecins, Rendez-vous, etc.)
- [x] API REST avec Django REST Framework
- [x] Authentification JWT
- [x] Documentation Swagger
- [x] Configuration CORS pour Flutter

### Phase 2 : Frontend Mobile (Flutter) 🔄 EN COURS
#### 2.1 Configuration de base
```bash
# Créer le projet Flutter
flutter create trimed_app
cd trimed_app

# Ajouter les dépendances
flutter pub add http shared_preferences provider
```

#### 2.2 Structure des dossiers
```
lib/
├── main.dart
├── services/
│   ├── api_service.dart
│   └── auth_service.dart
├── models/
│   ├── user.dart
│   ├── patient.dart
│   └── appointment.dart
├── screens/
│   ├── login_screen.dart
│   ├── home_screen.dart
│   ├── patients_screen.dart
│   └── appointments_screen.dart
└── widgets/
    ├── custom_button.dart
    └── loading_widget.dart
```

#### 2.3 Fonctionnalités principales
- [ ] Écran de connexion
- [ ] Dashboard principal
- [ ] Gestion des patients
- [ ] Gestion des rendez-vous
- [ ] Profil utilisateur

### Phase 3 : Intégration Backend ↔ Frontend
#### 3.1 Configuration réseau
```dart
// Configuration API
class ApiConfig {
  static const String baseUrl = 'http://10.0.2.2:8000'; // Émulateur
  // static const String baseUrl = 'http://192.168.1.XXX:8000'; // Appareil physique
}
```

#### 3.2 Service d'authentification
```dart
class AuthService {
  static Future<bool> login(String email, String password) async {
    // Connexion à l'API Django
    // Stockage des tokens JWT
    // Gestion des erreurs
  }
}
```

### Phase 4 : Fonctionnalités avancées
- [ ] Notifications push
- [ ] Mode hors ligne
- [ ] Synchronisation des données
- [ ] Rapports et statistiques
- [ ] Gestion des fichiers/images

### Phase 5 : Tests et déploiement
- [ ] Tests unitaires Flutter
- [ ] Tests d'intégration API
- [ ] Build APK/iOS
- [ ] Déploiement serveur

## 🚀 Prochaines étapes immédiates

### 1. Démarrer le Backend (MAINTENANT)
```bash
cd trimed_backend
python start_clean.py
```

### 2. Créer le projet Flutter
```bash
# Dans un nouveau terminal
flutter create trimed_app
cd trimed_app
```

### 3. Configurer Flutter pour l'API
```dart
// pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  shared_preferences: ^2.2.2
  provider: ^6.1.1
```

### 4. Créer le service API
```dart
// lib/services/api_service.dart
class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000';
  
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/comptes/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur de connexion');
    }
  }
}
```

### 5. Créer l'écran de connexion
```dart
// lib/screens/login_screen.dart
class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  Future<void> _login() async {
    try {
      final result = await ApiService.login(
        _emailController.text,
        _passwordController.text,
      );
      // Naviguer vers l'écran principal
      Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      // Afficher l'erreur
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: $e')),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Connexion Trimed')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _emailController,
              decoration: InputDecoration(labelText: 'Email'),
            ),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Mot de passe'),
              obscureText: true,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _login,
              child: Text('Se connecter'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 📱 Données de test

### Backend Django
- **URL**: http://10.0.2.2:8000
- **Email**: test@example.com
- **Password**: password123

### Endpoints disponibles
- `POST /api/comptes/login/` - Connexion
- `GET /api/comptes/utilisateurs/profile/` - Profil
- `GET /health/` - Test de santé
- `GET /swagger/` - Documentation

## 🎯 Objectifs par semaine

### Semaine 1 : Base fonctionnelle
- [x] Backend Django opérationnel
- [ ] Flutter avec écran de connexion
- [ ] Connexion Backend ↔ Frontend

### Semaine 2 : Fonctionnalités principales
- [ ] Gestion des patients
- [ ] Gestion des rendez-vous
- [ ] Navigation entre écrans

### Semaine 3 : Amélioration UX
- [ ] Design et animations
- [ ] Gestion des erreurs
- [ ] Mode hors ligne

### Semaine 4 : Finalisation
- [ ] Tests complets
- [ ] Optimisations
- [ ] Préparation déploiement

Votre backend est prêt ! Passez maintenant à la création de l'application Flutter.