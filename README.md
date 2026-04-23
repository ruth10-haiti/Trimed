# Trimed Backend API

API backend pour l'application de gestion hospitalière Trimed, développée avec Django REST Framework.

## 🚀 Démarrage rapide

### Prérequis
- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. **Cloner le projet** (si applicable)
```bash
git clone <repository-url>
cd trimed_backend
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données**
- Créer une base de données PostgreSQL nommée `Trimedh_BD`
- Créer un utilisateur `admin_Trimedh` avec le mot de passe `root`
- Ou modifier les paramètres dans `settings.py`

5. **Appliquer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Démarrer le serveur**
```bash
python manage.py runserver 0.0.0.0:8000
```

### 🎯 Démarrage automatique
Utilisez le script de démarrage automatique :
```bash
python start_dev.py
```

## 📚 Documentation API

Une fois le serveur démarré, accédez à :
- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/
- **Admin Django**: http://127.0.0.1:8000/admin/

## 🔗 Endpoints principaux

### Authentification
- `POST /api/comptes/login/` - Connexion
- `POST /api/comptes/inscription/` - Inscription
- `POST /api/comptes/logout/` - Déconnexion
- `POST /api/comptes/token/refresh/` - Rafraîchir le token

### Gestion des utilisateurs
- `GET /api/comptes/utilisateurs/` - Liste des utilisateurs
- `GET /api/comptes/utilisateurs/profile/` - Profil utilisateur
- `PUT /api/comptes/utilisateurs/update_profile/` - Modifier le profil

### Patients
- `GET /api/patients/` - Liste des patients
- `POST /api/patients/` - Créer un patient
- `GET /api/patients/{id}/` - Détails d'un patient

### Rendez-vous
- `GET /api/rendez-vous/` - Liste des rendez-vous
- `POST /api/rendez-vous/` - Créer un rendez-vous
- `GET /api/rendez-vous/creneaux_disponibles/` - Créneaux disponibles

### Médicaments
- `GET /api/medicaments/` - Liste des médicaments
- `POST /api/medicaments/` - Ajouter un médicament
- `POST /api/medicaments/{id}/mettre_a_jour_stock/` - Mettre à jour le stock

## 🔧 Configuration pour Flutter

### CORS
Le projet est configuré pour accepter les requêtes depuis :
- `localhost:3000` (développement web)
- `127.0.0.1:8000` (serveur local)
- `10.0.2.2:8000` (émulateur Android)

### Authentification JWT
- **Access Token**: Valide 1 heure
- **Refresh Token**: Valide 7 jours
- **Header**: `Authorization: Bearer <token>`

### Exemple de requête depuis Flutter
```dart
final response = await http.post(
  Uri.parse('http://10.0.2.2:8000/api/comptes/login/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'email': 'user@example.com',
    'password': 'password123',
  }),
);
```

## 🏗️ Structure du projet

```
trimed_backend/
├── comptes/           # Gestion des utilisateurs et authentification
├── patients/          # Gestion des patients
├── medical/           # Consultations, médecins, examens
├── gestion_medicaments/  # Gestion des médicaments et stock
├── rendez_vous/       # Système de rendez-vous
├── facturation/       # Facturation et abonnements
├── notifications/     # Système de notifications
├── gestion_tenants/   # Multi-tenancy (hôpitaux)
└── trimed_backend/    # Configuration principale
```

## 🔒 Sécurité

- Authentification JWT
- Permissions basées sur les rôles
- Multi-tenancy (isolation des données par hôpital)
- Validation des données d'entrée
- CORS configuré pour Flutter

## 🐛 Dépannage

### Erreur de base de données
```bash
# Vérifier que PostgreSQL est démarré
# Vérifier les paramètres de connexion dans settings.py
```

### Erreur CORS
```bash
# Vérifier que corsheaders est installé
# Vérifier la configuration CORS dans settings.py
```

### Erreur de migration
```bash
python manage.py makemigrations --empty <app_name>
python manage.py migrate --fake-initial
```

## 📱 Intégration Flutter

### Configuration réseau
Pour tester avec un émulateur Android, utilisez `10.0.2.2:8000` au lieu de `localhost:8000`.

### Gestion des tokens
Stockez les tokens JWT de manière sécurisée dans Flutter (SharedPreferences ou flutter_secure_storage).

### Gestion des erreurs
L'API retourne des erreurs au format JSON standard :
```json
{
  "error": "Message d'erreur",
  "detail": "Détails supplémentaires"
}
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request


