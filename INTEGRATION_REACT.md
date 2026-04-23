# Guide d'Intégration React - État Actuel du Backend

## ✅ Ce qui FONCTIONNE actuellement

### 1. Authentification (100% fonctionnel)
```javascript
// Configuration API
const API_BASE_URL = 'http://localhost:8000/api';

// Login
const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/comptes/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data;
  }
  throw new Error('Login failed');
};

// Inscription
const register = async (userData) => {
  const response = await fetch(`${API_BASE_URL}/comptes/inscription/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  return response.json();
};

// Refresh Token
const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  const response = await fetch(`${API_BASE_URL}/comptes/token/refresh/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh }),
  });
  return response.json();
};
```

### 2. Gestion des Utilisateurs (80% fonctionnel)
```javascript
// Headers avec authentification
const getAuthHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json',
});

// Liste des utilisateurs
const getUsers = async () => {
  const response = await fetch(`${API_BASE_URL}/comptes/utilisateurs/`, {
    headers: getAuthHeaders(),
  });
  return response.json();
};

// Profil utilisateur
const getUserProfile = async () => {
  const response = await fetch(`${API_BASE_URL}/comptes/utilisateurs/profile/`, {
    headers: getAuthHeaders(),
  });
  return response.json();
};
```

### 3. CORS et Configuration (100% fonctionnel)
- CORS configuré pour React (localhost:3000)
- Headers d'authentification acceptés
- Émulateur Android supporté (10.0.2.2:8000)

## ❌ Ce qui NE FONCTIONNE PAS

### 1. Patients (0% fonctionnel)
```javascript
// ❌ Ces endpoints retournent 404
const getPatients = async () => {
  // ERREUR: Pas de ViewSet implémenté
  const response = await fetch(`${API_BASE_URL}/patients/`);
  return response.json(); // 404 Not Found
};
```

### 2. Rendez-vous (0% fonctionnel)
```javascript
// ❌ Ces endpoints n'existent pas
const getAppointments = async () => {
  // ERREUR: URLs vides
  const response = await fetch(`${API_BASE_URL}/rendez-vous/`);
  return response.json(); // 404 Not Found
};
```

### 3. Consultations Médicales (0% fonctionnel)
```javascript
// ❌ Module médical non implémenté
const getConsultations = async () => {
  const response = await fetch(`${API_BASE_URL}/medical/consultations/`);
  return response.json(); // 404 Not Found
};
```

## 🔧 Solutions de Contournement

### 1. Utiliser des Données Mock
```javascript
// services/mockData.js
export const mockPatients = [
  {
    id: 1,
    nom: 'Dupont',
    prenom: 'Jean',
    email: 'jean.dupont@email.com',
    telephone: '0123456789',
    date_naissance: '1980-01-01',
  },
  // ... autres patients
];

export const mockAppointments = [
  {
    id: 1,
    patient_id: 1,
    medecin: 'Dr. Martin',
    date_heure: '2024-01-15T10:00:00Z',
    motif: 'Consultation générale',
    statut: 'confirmé',
  },
  // ... autres RDV
];
```

### 2. Service API avec Fallback
```javascript
// services/apiService.js
class ApiService {
  constructor() {
    this.baseURL = 'http://localhost:8000/api';
    this.useMockData = true; // Activer les données mock
  }

  async getPatients() {
    if (this.useMockData) {
      return { results: mockPatients };
    }
    
    try {
      const response = await fetch(`${this.baseURL}/patients/`, {
        headers: getAuthHeaders(),
      });
      return response.json();
    } catch (error) {
      console.warn('API non disponible, utilisation des données mock');
      return { results: mockPatients };
    }
  }

  async getAppointments() {
    if (this.useMockData) {
      return { results: mockAppointments };
    }
    
    // Même logique pour les RDV
  }
}

export default new ApiService();
```

### 3. Hook React pour l'API
```javascript
// hooks/useApi.js
import { useState, useEffect } from 'react';
import ApiService from '../services/apiService';

export const usePatients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        const data = await ApiService.getPatients();
        setPatients(data.results || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  return { patients, loading, error };
};
```

## 🚀 Stratégie de Développement React

### Phase 1: Développement avec Mock Data
```javascript
// 1. Créer l'interface utilisateur complète
// 2. Utiliser des données mock pour tous les modules
// 3. Implémenter la logique métier côté frontend
// 4. Tester l'UX/UI sans dépendre du backend
```

### Phase 2: Intégration Progressive
```javascript
// 1. Connecter l'authentification (déjà fonctionnel)
// 2. Remplacer progressivement les mocks par les vrais endpoints
// 3. Gérer les erreurs et les cas d'échec
// 4. Optimiser les performances
```

## 📋 Checklist d'Intégration

### ✅ Prêt pour React
- [x] Authentification JWT
- [x] CORS configuré
- [x] Gestion des utilisateurs
- [x] Documentation Swagger basique

### ⏳ En Attente (Backend à développer)
- [ ] CRUD Patients
- [ ] CRUD Rendez-vous
- [ ] CRUD Consultations
- [ ] CRUD Médicaments
- [ ] Système de notifications
- [ ] Facturation

### 🔄 Recommandations

1. **Commencer par l'authentification**: Implémenter login/logout/register
2. **Utiliser des mocks**: Pour tous les autres modules
3. **Développer en parallèle**: Frontend avec mocks, Backend avec vrais endpoints
4. **Tests d'intégration**: Dès que les endpoints sont prêts
5. **Gestion d'erreurs**: Prévoir les cas où l'API n'est pas disponible

## 🎯 Exemple d'Application React Minimale

```javascript
// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Patients from './components/Patients';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

## 🔍 Résumé

**Oui, tu peux connecter React maintenant**, mais avec des limitations:

- ✅ **Authentification**: 100% fonctionnel
- ✅ **Utilisateurs**: 80% fonctionnel  
- ❌ **Patients**: 0% fonctionnel (utiliser des mocks)
- ❌ **Rendez-vous**: 0% fonctionnel (utiliser des mocks)
- ❌ **Consultations**: 0% fonctionnel (utiliser des mocks)

**Stratégie recommandée**: Développer le frontend avec des données mock en parallèle du développement backend.