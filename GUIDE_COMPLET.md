# Guide Complet : Django + PostgreSQL + Flutter

## Étape 1 : Configuration PostgreSQL

### 1.1 Installer PostgreSQL
- Télécharger depuis https://www.postgresql.org/download/windows/
- Installer avec le mot de passe `root` pour l'utilisateur `postgres`

### 1.2 Créer la base de données
**Option A - Avec pgAdmin :**
1. Ouvrir pgAdmin
2. Se connecter au serveur PostgreSQL
3. Clic droit sur "Databases" → "Create" → "Database"
4. Nom : `Trimedh_BD`
5. Owner : `postgres`

**Option B - Avec psql :**
```sql
-- Ouvrir psql et exécuter :
CREATE DATABASE "Trimedh_BD";
CREATE USER admin_Trimedh WITH PASSWORD 'root';
GRANT ALL PRIVILEGES ON DATABASE "Trimedh_BD" TO admin_Trimedh;
```

## Étape 2 : Configuration Django

### 2.1 Vérifier les paramètres
Le fichier `settings.py` est déjà configuré :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Trimedh_BD',
        'USER': 'admin_Trimedh',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2.2 Installation et configuration
```bash
# 1. Aller dans le dossier backend
cd c:\Users\ruth\AndroidStudioProjects\trimed_hApp\trimed_h\trimed_backend

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configuration complète automatique
python setup_complete.py
```

## Étape 3 : Démarrer le serveur

```bash
# Démarrer le serveur Django
python manage.py runserver 0.0.0.0:8000
```

**Vérifications :**
- http://127.0.0.1:8000/health/ → `{"status": "OK"}`
- http://127.0.0.1:8000/admin/ → Interface d'administration
- http://127.0.0.1:8000/swagger/ → Documentation API

## Étape 4 : Test avec Flutter

### 4.1 Configuration Flutter
Dans `pubspec.yaml` :
```yaml
dependencies:
  http: ^1.1.0
  shared_preferences: ^2.2.2
```

### 4.2 Service API Flutter
```dart
// lib/services/api_service.dart
class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000'; // Émulateur
  // static const String baseUrl = 'http://192.168.1.XXX:8000'; // Appareil physique
  
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/comptes/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur: ${response.body}');
    }
  }
}
```

### 4.3 Test de connexion
```dart
// Test avec les données créées
try {
  final result = await ApiService.login('test@example.com', 'password123');
  print('✅ Connexion réussie: ${result['utilisateur']['nom_complet']}');
} catch (e) {
  print('❌ Erreur: $e');
}
```

## Étape 5 : Données de test disponibles

Après `python setup_complete.py`, vous aurez :

**Utilisateur normal :**
- Email : `test@example.com`
- Mot de passe : `password123`
- Rôle : `patient`

**Administrateur :**
- Email : `admin@example.com`
- Mot de passe : `admin123`
- Rôle : `admin-systeme`

**Hôpital de test :**
- Nom : "Hôpital de Test"
- Adresse : "123 Rue de Test"

## Étape 6 : Endpoints principaux

### Authentification
```
POST /api/comptes/login/
POST /api/comptes/inscription/
POST /api/comptes/logout/
POST /api/comptes/token/refresh/
```

### Utilisateurs
```
GET /api/comptes/utilisateurs/
GET /api/comptes/utilisateurs/profile/
PUT /api/comptes/utilisateurs/update_profile/
```

### Patients
```
GET /api/patients/
POST /api/patients/
GET /api/patients/{id}/
```

## Dépannage

### Erreur de connexion PostgreSQL
```bash
# Vérifier que PostgreSQL est démarré
# Vérifier les paramètres dans settings.py
# Tester la connexion :
psql -h localhost -U admin_Trimedh -d Trimedh_BD
```

### Erreur de migration
```bash
python manage.py makemigrations --empty comptes
python manage.py migrate --fake-initial
```

### Erreur CORS Flutter
- Vérifier l'URL : `http://10.0.2.2:8000` pour émulateur
- Pour appareil physique : `http://[IP_DE_VOTRE_PC]:8000`

## Test final

1. **Backend** : `python manage.py runserver 0.0.0.0:8000`
2. **Test API** : `python test_api.py`
3. **Flutter** : Utiliser les données de test ci-dessus

✅ **Succès** : Vous devriez recevoir un token JWT et les données utilisateur
❌ **Échec** : Vérifier les logs Django et la connectivité réseau