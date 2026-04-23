# 🚀 Roadmap Migration React: JSON Server → Django Backend

## 📋 Vue d'ensemble
Guide complet pour migrer votre frontend React de JSON Server vers le nouveau backend Django Trimed.

## 🔄 Changements Principaux

### 1. **URLs de Base**
```javascript
// AVANT (JSON Server)
const BASE_URL = 'http://localhost:3001'

// APRÈS (Django)
const BASE_URL = 'http://localhost:8000/api'
// ou pour émulateur Android
const BASE_URL = 'http://10.0.2.2:8000/api'
```

### 2. **Authentification**
```javascript
// AVANT (JSON Server - simulation)
localStorage.setItem('user', JSON.stringify(userData))

// APRÈS (Django JWT)
// Login
const response = await fetch(`${BASE_URL}/comptes/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})
const { access, refresh, user } = await response.json()
localStorage.setItem('access_token', access)
localStorage.setItem('refresh_token', refresh)
```

## 🗂️ Migration par Module

### 📊 1. Authentification & Comptes

#### Endpoints à changer:
```javascript
// AVANT
POST /users          → POST /api/comptes/inscription/
POST /login          → POST /api/comptes/login/
GET  /users/:id      → GET  /api/comptes/utilisateurs/profile/

// NOUVEAU
POST /api/comptes/inscription/
POST /api/comptes/login/
POST /api/comptes/logout/
POST /api/comptes/token/refresh/
GET  /api/comptes/utilisateurs/profile/
PUT  /api/comptes/utilisateurs/update_profile/
```

#### Service React à modifier:
```javascript
// services/authService.js
class AuthService {
  async login(email, password) {
    const response = await fetch(`${BASE_URL}/comptes/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    
    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      return data
    }
    throw new Error('Login failed')
  }

  async register(userData) {
    const response = await fetch(`${BASE_URL}/comptes/inscription/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })
    return response.json()
  }

  getAuthHeaders() {
    const token = localStorage.getItem('access_token')
    return token ? { 'Authorization': `Bearer ${token}` } : {}
  }
}
```

### 🏥 2. Patients

#### Endpoints à changer:
```javascript
// AVANT
GET  /patients           → GET  /api/patients/
POST /patients           → POST /api/patients/
GET  /patients/:id       → GET  /api/patients/:id/
PUT  /patients/:id       → PUT  /api/patients/:id/

// NOUVEAUX endpoints disponibles
GET  /api/patients/:id/dossier_complet/
POST /api/patients/:id/ajouter_allergie/
POST /api/patients/:id/ajouter_antecedent/
GET  /api/patients/statistiques/
```

#### Service React:
```javascript
// services/patientService.js
class PatientService {
  async getPatients(filters = {}) {
    const params = new URLSearchParams(filters)
    const response = await fetch(`${BASE_URL}/patients/?${params}`, {
      headers: { ...authService.getAuthHeaders() }
    })
    return response.json()
  }

  async createPatient(patientData) {
    const response = await fetch(`${BASE_URL}/patients/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders()
      },
      body: JSON.stringify(patientData)
    })
    return response.json()
  }

  async getDossierComplet(patientId) {
    const response = await fetch(`${BASE_URL}/patients/${patientId}/dossier_complet/`, {
      headers: { ...authService.getAuthHeaders() }
    })
    return response.json()
  }
}
```

### 📅 3. Rendez-vous

#### Endpoints à changer:
```javascript
// AVANT
GET  /appointments      → GET  /api/rendez-vous/
POST /appointments      → POST /api/rendez-vous/

// NOUVEAUX endpoints
GET  /api/rendez-vous/creneaux_disponibles/
POST /api/rendez-vous/:id/confirmer/
POST /api/rendez-vous/:id/annuler/
POST /api/rendez-vous/:id/reporter/
```

#### Service React:
```javascript
// services/appointmentService.js
class AppointmentService {
  async getCreneauxDisponibles(medecinId, date) {
    const response = await fetch(
      `${BASE_URL}/rendez-vous/creneaux_disponibles/?medecin=${medecinId}&date=${date}`,
      { headers: { ...authService.getAuthHeaders() } }
    )
    return response.json()
  }

  async createRendezVous(rdvData) {
    const response = await fetch(`${BASE_URL}/rendez-vous/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders()
      },
      body: JSON.stringify(rdvData)
    })
    return response.json()
  }
}
```

### 🩺 4. Medical (Nouveau Module)

#### Nouveaux endpoints disponibles:
```javascript
// Médecins
GET  /api/medical/medecins/
POST /api/medical/medecins/
GET  /api/medical/medecins/:id/statistiques/

// Consultations
GET  /api/medical/consultations/
POST /api/medical/consultations/
POST /api/medical/consultations/:id/creer_ordonnance/

// Examens
GET  /api/medical/examens/
POST /api/medical/examens/
PUT  /api/medical/examens/:id/ajouter_resultat/
```

#### Service React:
```javascript
// services/medicalService.js
class MedicalService {
  async getMedecins() {
    const response = await fetch(`${BASE_URL}/medical/medecins/`, {
      headers: { ...authService.getAuthHeaders() }
    })
    return response.json()
  }

  async createConsultation(consultationData) {
    const response = await fetch(`${BASE_URL}/medical/consultations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders()
      },
      body: JSON.stringify(consultationData)
    })
    return response.json()
  }
}
```

### 💊 5. Médicaments (Nouveau Module)

#### Endpoints disponibles:
```javascript
GET  /api/medicaments/
POST /api/medicaments/
PUT  /api/medicaments/:id/
POST /api/medicaments/:id/mettre_a_jour_stock/
GET  /api/medicaments/categories/
GET  /api/medicaments/stock_faible/
GET  /api/medicaments/statistiques/
```

## 🔧 Modifications Techniques Requises

### 1. **Intercepteur HTTP pour JWT**
```javascript
// utils/httpInterceptor.js
class HttpInterceptor {
  static async request(url, options = {}) {
    const token = localStorage.getItem('access_token')
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
      }
    }

    let response = await fetch(url, config)
    
    // Auto-refresh token si expiré
    if (response.status === 401) {
      const refreshed = await this.refreshToken()
      if (refreshed) {
        config.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`
        response = await fetch(url, config)
      }
    }
    
    return response
  }

  static async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) return false

    try {
      const response = await fetch(`${BASE_URL}/comptes/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      })

      if (response.ok) {
        const { access } = await response.json()
        localStorage.setItem('access_token', access)
        return true
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
    }
    
    // Redirect to login
    localStorage.clear()
    window.location.href = '/login'
    return false
  }
}
```

### 2. **Context Provider pour l'état global**
```javascript
// contexts/AppContext.js
import React, { createContext, useContext, useReducer } from 'react'

const AppContext = createContext()

const initialState = {
  user: null,
  isAuthenticated: false,
  patients: [],
  appointments: [],
  loading: false,
  error: null
}

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload, isAuthenticated: true }
    case 'SET_PATIENTS':
      return { ...state, patients: action.payload }
    case 'ADD_PATIENT':
      return { ...state, patients: [...state.patients, action.payload] }
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    case 'LOGOUT':
      return { ...initialState }
    default:
      return state
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState)
  
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => useContext(AppContext)
```

### 3. **Hook personnalisé pour les API calls**
```javascript
// hooks/useApi.js
import { useState, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'

export function useApi(apiCall, dependencies = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { dispatch } = useApp()

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)
        const result = await apiCall()
        setData(result)
      } catch (err) {
        setError(err.message)
        dispatch({ type: 'SET_ERROR', payload: err.message })
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, dependencies)

  return { data, loading, error, refetch: () => fetchData() }
}
```

## 📝 Plan de Migration Étape par Étape

### Phase 1: Configuration de Base (1-2 jours)
1. ✅ Changer BASE_URL
2. ✅ Implémenter HttpInterceptor
3. ✅ Créer AuthService
4. ✅ Tester login/logout

### Phase 2: Migration Patients (2-3 jours)
1. ✅ Modifier PatientService
2. ✅ Adapter les composants patients
3. ✅ Tester CRUD patients
4. ✅ Implémenter nouvelles fonctionnalités (dossier complet, allergies)

### Phase 3: Migration Rendez-vous (2-3 jours)
1. ✅ Modifier AppointmentService
2. ✅ Adapter calendrier/planning
3. ✅ Implémenter créneaux disponibles
4. ✅ Tester workflow complet

### Phase 4: Nouveaux Modules (3-4 jours)
1. ✅ Créer MedicalService
2. ✅ Créer MedicamentService
3. ✅ Développer nouveaux composants
4. ✅ Intégrer workflow médical

### Phase 5: Tests & Optimisation (2-3 jours)
1. ✅ Tests end-to-end
2. ✅ Gestion d'erreurs
3. ✅ Performance
4. ✅ UX/UI polish

## 🚨 Points d'Attention

### Gestion des Erreurs
```javascript
// utils/errorHandler.js
export function handleApiError(error, dispatch) {
  if (error.status === 401) {
    dispatch({ type: 'LOGOUT' })
    window.location.href = '/login'
  } else if (error.status === 403) {
    dispatch({ type: 'SET_ERROR', payload: 'Accès non autorisé' })
  } else {
    dispatch({ type: 'SET_ERROR', payload: error.message })
  }
}
```

### Validation des Formulaires
```javascript
// utils/validation.js
export const patientValidation = {
  nom: { required: true, minLength: 2 },
  prenom: { required: true, minLength: 2 },
  email: { required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
  telephone: { required: true, pattern: /^[0-9+\-\s()]+$/ }
}
```

## 📊 Checklist de Migration

### Authentification
- [ ] Login/Logout fonctionnel
- [ ] Auto-refresh token
- [ ] Gestion des permissions
- [ ] Redirection après expiration

### Patients
- [ ] Liste patients avec pagination
- [ ] Création/modification patient
- [ ] Dossier médical complet
- [ ] Gestion allergies/antécédents

### Rendez-vous
- [ ] Calendrier interactif
- [ ] Créneaux disponibles
- [ ] Confirmation/annulation RDV
- [ ] Notifications

### Nouveaux Modules
- [ ] Interface médecins
- [ ] Consultations médicales
- [ ] Gestion médicaments
- [ ] Statistiques

### Performance
- [ ] Lazy loading
- [ ] Cache des données
- [ ] Optimisation des requêtes
- [ ] Loading states

---

**Estimation totale**: 10-15 jours de développement
**Complexité**: Moyenne à élevée
**Impact**: Migration complète vers architecture production