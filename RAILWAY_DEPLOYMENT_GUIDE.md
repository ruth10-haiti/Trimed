# 🚀 Guide Déploiement Railway - Trimed Backend

## 📋 Prérequis
- Compte Railway (railway.app)
- Code pushé sur GitHub
- PostgreSQL configuré

## 🔧 Configuration Railway

### 1. **Créer Nouveau Projet**
```bash
# Sur railway.app
1. New Project
2. Deploy from GitHub repo
3. Sélectionner votre repo trimed_backend
```

### 2. **Ajouter PostgreSQL**
```bash
# Dans votre projet Railway
1. New Service
2. Database
3. PostgreSQL
4. Deploy
```

### 3. **Variables d'Environnement**
```bash
# Dans Settings > Environment Variables
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

### 4. **Configuration Automatique**
Railway va automatiquement:
- Détecter requirements.txt
- Installer les dépendances
- Configurer DATABASE_URL
- Déployer l'application

## 🗄️ Configuration PostgreSQL

### Variables Automatiques Railway:
```bash
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
PGHOST=postgres.railway.internal
PGPORT=5432
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=auto-generated-password
```

### Notre Configuration (settings.py):
```python
# Détection automatique Railway
if os.environ.get('DATABASE_URL'):
    # Production (Railway)
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Development local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'Trimedh_BD',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
```

## 🚀 Commandes de Déploiement

### Build Command (Automatique):
```bash
pip install -r requirements.txt
```

### Start Command (railway.toml):
```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn trimed_backend.wsgi:application
```

## ✅ Checklist Déploiement

### Avant Déploiement:
- [ ] requirements.txt à jour avec psycopg2-binary
- [ ] settings.py configuré pour production
- [ ] railway.toml créé
- [ ] Variables d'environnement définies
- [ ] Code pushé sur GitHub

### Après Déploiement:
- [ ] Migrations appliquées automatiquement
- [ ] Static files collectés
- [ ] Base de données accessible
- [ ] API endpoints fonctionnels
- [ ] CORS configuré pour frontend

## 🔍 Vérification Post-Déploiement

### 1. **Tester l'API**
```bash
# URL de base
https://your-app-name.up.railway.app/api/

# Test endpoints
GET https://your-app-name.up.railway.app/api/comptes/
POST https://your-app-name.up.railway.app/api/comptes/login/
```

### 2. **Vérifier Base de Données**
```bash
# Dans Railway Dashboard > PostgreSQL > Connect
# Ou utiliser l'URL de connexion fournie
```

### 3. **Logs de Déploiement**
```bash
# Dans Railway Dashboard > Deployments > View Logs
# Vérifier les erreurs de migration ou configuration
```

## 🛠️ Dépannage Courant

### Erreur de Migration:
```bash
# Solution: Redéployer avec migrations
railway run python manage.py migrate --run-syncdb
```

### Erreur Static Files:
```bash
# Solution: Vérifier STATIC_ROOT dans settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

### Erreur CORS:
```bash
# Solution: Ajouter domaine Railway dans CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "https://your-app.up.railway.app"
]
```

### Erreur Database Connection:
```bash
# Vérifier que PostgreSQL service est déployé
# Vérifier DATABASE_URL dans variables d'environnement
```

## 📊 Monitoring

### Métriques Railway:
- CPU Usage
- Memory Usage
- Network Traffic
- Database Connections

### Logs Application:
```bash
# Accès via Railway Dashboard
# Ou via CLI: railway logs
```

## 🔐 Sécurité Production

### Variables Sensibles:
```bash
SECRET_KEY=generate-new-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app
```

### HTTPS Automatique:
Railway fournit automatiquement HTTPS pour tous les déploiements.

## 💡 Optimisations

### Performance:
- Utiliser gunicorn avec workers multiples
- Configurer cache Redis si nécessaire
- Optimiser requêtes ORM

### Coûts:
- Railway offre $5 de crédit gratuit/mois
- PostgreSQL: ~$5/mois
- Web service: ~$5/mois

---

**Avec cette configuration, votre backend Django sera déployé automatiquement sur Railway avec PostgreSQL!**