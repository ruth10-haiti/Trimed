# 🔑 Enfomasyon Krisyal Backend Django pou Entegrasyon React

## 📋 Enfomasyon Esansyèl yo

### 1. **🌐 URLs ak Endpoints**

#### Base URL:
```
http://localhost:8000/api/
```

#### Tout Endpoints yo:
```
📊 AUTHENTICATION
POST /api/comptes/inscription/
POST /api/comptes/login/
POST /api/comptes/logout/
POST /api/comptes/token/refresh/
GET  /api/comptes/utilisateurs/profile/
PUT  /api/comptes/utilisateurs/update_profile/

🏥 PATIENTS  
GET  /api/patients/
POST /api/patients/
GET  /api/patients/{id}/
PUT  /api/patients/{id}/
DELETE /api/patients/{id}/
GET  /api/patients/{id}/dossier_complet/
POST /api/patients/{id}/ajouter_allergie/
POST /api/patients/{id}/ajouter_antecedent/
GET  /api/patients/statistiques/

📅 RENDEZ-VOUS
GET  /api/rendez-vous/
POST /api/rendez-vous/
GET  /api/rendez-vous/{id}/
PUT  /api/rendez-vous/{id}/
DELETE /api/rendez-vous/{id}/
GET  /api/rendez-vous/creneaux_disponibles/
POST /api/rendez-vous/{id}/confirmer/
POST /api/rendez-vous/{id}/annuler/
POST /api/rendez-vous/{id}/reporter/
GET  /api/rendez-vous/statistiques/

🩺 MEDICAL
GET  /api/medical/medecins/
POST /api/medical/medecins/
GET  /api/medical/medecins/{id}/statistiques/
GET  /api/medical/consultations/
POST /api/medical/consultations/
GET  /api/medical/consultations/{id}/
POST /api/medical/consultations/{id}/creer_ordonnance/
GET  /api/medical/examens/
POST /api/medical/examens/
PUT  /api/medical/examens/{id}/ajouter_resultat/

💊 MEDICAMENTS
GET  /api/medicaments/
POST /api/medicaments/
PUT  /api/medicaments/{id}/
POST /api/medicaments/{id}/mettre_a_jour_stock/
GET  /api/medicaments/categories/
GET  /api/medicaments/stock_faible/
GET  /api/medicaments/statistiques/
```

### 2. **🔐 Sistèm Otentifikasyon**

#### JWT Token System:
```javascript
// Login Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nom": "Doe",
    "prenom": "John",
    "role": "medecin",
    "hopital": {
      "id": 1,
      "nom": "Hôpital Central"
    }
  }
}
```

#### Headers Required:
```javascript
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <access_token>"
}
```

### 3. **👥 Sistèm Permissions ak Roles**

#### 6 Roles yo:
```javascript
const ROLES = {
  ADMIN_SYSTEME: 'admin-systeme',        // Tout aksè
  PROPRIETAIRE_HOPITAL: 'proprietaire-hopital', // Jesyon lopital
  MEDECIN: 'medecin',                    // Konsèltasyon, òdonnans
  INFIRMIER: 'infirmier',                // Swiv pasyan yo
  SECRETAIRE: 'secretaire',              // RDV, resepsyon
  PATIENT: 'patient'                     // Wè done pèsonèl yo sèlman
}
```

#### Permissions Matrix:
```javascript
const PERMISSIONS = {
  patients: {
    'admin-systeme': ['create', 'read', 'update', 'delete'],
    'proprietaire-hopital': ['create', 'read', 'update', 'delete'],
    'medecin': ['create', 'read', 'update', 'delete'],
    'infirmier': ['read', 'update'],
    'secretaire': ['read'],
    'patient': ['read_own']
  },
  consultations: {
    'medecin': ['create', 'read', 'update'],
    'infirmier': ['read'],
    'patient': ['read_own']
  }
}
```

### 4. **📊 Fòma Done yo (Data Formats)**

#### Patient Object:
```javascript
{
  "id": 1,
  "nom": "Doe",
  "prenom": "John",
  "email": "john@example.com",
  "telephone": "+509 1234-5678",
  "date_naissance": "1990-01-15",
  "sexe": "M",
  "age": 34,
  "imc": 24.5,
  "adresse": {
    "rue": "123 Main St",
    "ville": "Port-au-Prince",
    "departement": "Ouest",
    "code_postal": "HT1234"
  },
  "assurance": {
    "compagnie": "Assurance Santé",
    "numero_police": "AS123456"
  },
  "allergies": ["Pénicilline", "Arachides"],
  "antecedents": ["Hypertension", "Diabète"]
}
```

#### Rendez-vous Object:
```javascript
{
  "id": 1,
  "patient": 1,
  "medecin": 2,
  "date_heure": "2024-01-15T10:30:00Z",
  "motif": "Consultation générale",
  "statut": "confirme",
  "notes": "Patient en bonne santé",
  "duree_minutes": 30
}
```

#### Consultation Object:
```javascript
{
  "id": 1,
  "patient": 1,
  "medecin": 2,
  "date_consultation": "2024-01-15T10:30:00Z",
  "motif": "Douleur abdominale",
  "diagnostic": "Gastrite",
  "traitement": "Repos et médicaments",
  "notes": "Suivi dans 2 semaines",
  "ordonnances": [
    {
      "medicament": "Oméprazole",
      "dosage": "20mg",
      "frequence": "2 fois par jour",
      "duree": "7 jours"
    }
  ]
}
```

### 5. **⚠️ Jesyon Erè yo (Error Handling)**

#### Standard Error Format:
```javascript
// 400 Bad Request
{
  "error": "Validation failed",
  "details": {
    "email": ["This field is required"],
    "telephone": ["Invalid phone number format"]
  }
}

// 401 Unauthorized
{
  "error": "Authentication required",
  "detail": "Token has expired"
}

// 403 Forbidden
{
  "error": "Permission denied",
  "detail": "You don't have permission to access this resource"
}

// 404 Not Found
{
  "error": "Resource not found",
  "detail": "Patient with id 999 does not exist"
}

// 500 Server Error
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred"
}
```

### 6. **📄 Pagination Format**

#### List Response Format:
```javascript
{
  "count": 150,
  "next": "http://localhost:8000/api/patients/?page=3",
  "previous": "http://localhost:8000/api/patients/?page=1",
  "results": [
    // Array of objects
  ]
}
```

#### Query Parameters:
```javascript
// Pagination
?page=2&page_size=20

// Search
?search=john

// Filtering
?sexe=M&age_min=18&age_max=65

// Ordering
?ordering=-date_creation
```

### 7. **🔍 Rechèch ak Filtè yo**

#### Available Filters:
```javascript
// Patients
?search=nom,prenom,email
?sexe=M|F
?age_min=18&age_max=65
?ville=Port-au-Prince

// Rendez-vous
?date_debut=2024-01-01&date_fin=2024-01-31
?medecin=1
?statut=confirme|en_attente|annule

// Consultations
?patient=1
?medecin=2
?date_debut=2024-01-01
```

### 8. **📊 Validation Rules**

#### Required Fields:
```javascript
// Patient Creation
{
  "nom": "required, min_length=2",
  "prenom": "required, min_length=2", 
  "email": "required, valid_email, unique",
  "telephone": "required, valid_phone",
  "date_naissance": "required, date, not_future",
  "sexe": "required, choices=['M', 'F']"
}

// Rendez-vous Creation
{
  "patient": "required, exists",
  "medecin": "required, exists",
  "date_heure": "required, datetime, future, business_hours",
  "motif": "required, min_length=5"
}
```

#### Business Rules:
```javascript
// Rendez-vous
- Pa ka kreye RDV nan pase a
- RDV yo dwe nan èdtan travay (8h-18h)
- Pa gen RDV dimanch
- Pa ka gen 2 RDV nan menm tan pou menm moun

// Consultations  
- Sèlman medecin yo ka kreye konsèltasyon
- Konsèltasyon dwe gen yon RDV ki egziste deja
```

### 9. **🚀 Performance Tips**

#### Optimized Queries:
```javascript
// Use these parameters for better performance
?select_related=patient,medecin
?prefetch_related=allergies,antecedents

// Limit fields returned
?fields=id,nom,prenom,email
```

#### Caching:
```javascript
// These endpoints are cached for 5 minutes
GET /api/medical/medecins/
GET /api/medicaments/categories/
GET /api/comptes/utilisateurs/profile/
```

### 10. **🔧 Development vs Production**

#### Development URLs:
```javascript
const BASE_URL = 'http://localhost:8000/api'
```

#### Production URLs:
```javascript
const BASE_URL = 'https://your-domain.com/api'
```

#### CORS Settings:
```javascript
// Allowed origins for CORS
const ALLOWED_ORIGINS = [
  'http://localhost:3000',    // React dev server
  'http://127.0.0.1:3000',   // Alternative localhost
  'http://10.0.2.2:8000',    // Android emulator
]
```

## 🎯 Enfomasyon Kritik yo pou React

### 1. **Mandatory Headers**
```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${access_token}`
}
```

### 2. **Token Refresh Logic**
```javascript
// Check if token needs refresh every 5 minutes
setInterval(checkTokenExpiry, 5 * 60 * 1000)
```

### 3. **Multi-tenant Awareness**
```javascript
// All data is automatically filtered by user's hospital
// No need to pass hospital_id in requests
```

### 4. **Required Environment Variables**
```javascript
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

---

**Ak enfomasyon sa yo, ou ka entegre nenpòt frontend React ak backend Django a san pwoblèm!**