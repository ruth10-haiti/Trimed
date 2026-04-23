# 🔧 Exemples de Code React - Migration JSON Server → Django

## 📋 Composants React à Modifier

### 1. **Login Component**

#### AVANT (JSON Server)
```javascript
// components/Login.js
import React, { useState } from 'react'

function Login() {
  const [credentials, setCredentials] = useState({ email: '', password: '' })

  const handleLogin = async (e) => {
    e.preventDefault()
    // Simulation avec JSON Server
    const response = await fetch('http://localhost:3001/users')
    const users = await response.json()
    const user = users.find(u => u.email === credentials.email)
    
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
      window.location.href = '/dashboard'
    }
  }

  return (
    <form onSubmit={handleLogin}>
      <input 
        type="email" 
        value={credentials.email}
        onChange={(e) => setCredentials({...credentials, email: e.target.value})}
      />
      <input 
        type="password" 
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
      />
      <button type="submit">Se connecter</button>
    </form>
  )
}
```

#### APRÈS (Django JWT)
```javascript
// components/Login.js
import React, { useState } from 'react'
import { useApp } from '../contexts/AppContext'
import { authService } from '../services/authService'

function Login() {
  const [credentials, setCredentials] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { dispatch } = useApp()

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authService.login(credentials.email, credentials.password)
      dispatch({ type: 'SET_USER', payload: response.user })
      window.location.href = '/dashboard'
    } catch (err) {
      setError('Email ou mot de passe incorrect')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleLogin}>
      {error && <div className="error">{error}</div>}
      <input 
        type="email" 
        value={credentials.email}
        onChange={(e) => setCredentials({...credentials, email: e.target.value})}
        required
      />
      <input 
        type="password" 
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Connexion...' : 'Se connecter'}
      </button>
    </form>
  )
}
```

### 2. **Patient List Component**

#### AVANT (JSON Server)
```javascript
// components/PatientList.js
import React, { useState, useEffect } from 'react'

function PatientList() {
  const [patients, setPatients] = useState([])

  useEffect(() => {
    fetch('http://localhost:3001/patients')
      .then(res => res.json())
      .then(data => setPatients(data))
  }, [])

  return (
    <div>
      <h2>Liste des Patients</h2>
      {patients.map(patient => (
        <div key={patient.id}>
          <h3>{patient.nom} {patient.prenom}</h3>
          <p>{patient.email}</p>
        </div>
      ))}
    </div>
  )
}
```

#### APRÈS (Django API)
```javascript
// components/PatientList.js
import React, { useState, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'
import { patientService } from '../services/patientService'

function PatientList() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ search: '', page: 1 })
  const [pagination, setPagination] = useState({})
  const { state, dispatch } = useApp()

  useEffect(() => {
    loadPatients()
  }, [filters])

  const loadPatients = async () => {
    try {
      setLoading(true)
      const response = await patientService.getPatients(filters)
      setPatients(response.results)
      setPagination({
        count: response.count,
        next: response.next,
        previous: response.previous
      })
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Erreur lors du chargement des patients' })
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    setFilters({ ...filters, search: e.target.value, page: 1 })
  }

  const viewDossierComplet = async (patientId) => {
    try {
      const dossier = await patientService.getDossierComplet(patientId)
      // Ouvrir modal ou naviguer vers page détail
      console.log('Dossier complet:', dossier)
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Erreur lors du chargement du dossier' })
    }
  }

  if (loading) return <div>Chargement...</div>

  return (
    <div>
      <h2>Liste des Patients ({pagination.count})</h2>
      
      <input 
        type="text" 
        placeholder="Rechercher un patient..."
        value={filters.search}
        onChange={handleSearch}
      />

      {patients.map(patient => (
        <div key={patient.id} className="patient-card">
          <h3>{patient.nom} {patient.prenom}</h3>
          <p>📧 {patient.email}</p>
          <p>📞 {patient.telephone}</p>
          <p>🎂 {patient.age} ans</p>
          {patient.imc && <p>📊 IMC: {patient.imc}</p>}
          
          <div className="actions">
            <button onClick={() => viewDossierComplet(patient.id)}>
              Dossier Complet
            </button>
            <button>Modifier</button>
          </div>
        </div>
      ))}

      {/* Pagination */}
      <div className="pagination">
        <button 
          disabled={!pagination.previous}
          onClick={() => setFilters({...filters, page: filters.page - 1})}
        >
          Précédent
        </button>
        <span>Page {filters.page}</span>
        <button 
          disabled={!pagination.next}
          onClick={() => setFilters({...filters, page: filters.page + 1})}
        >
          Suivant
        </button>
      </div>
    </div>
  )
}
```

### 3. **Appointment Booking Component**

#### AVANT (JSON Server)
```javascript
// components/AppointmentBooking.js
import React, { useState } from 'react'

function AppointmentBooking() {
  const [appointment, setAppointment] = useState({
    patientId: '',
    doctorId: '',
    date: '',
    time: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    await fetch('http://localhost:3001/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appointment)
    })
    alert('Rendez-vous créé!')
  }

  return (
    <form onSubmit={handleSubmit}>
      <select onChange={(e) => setAppointment({...appointment, patientId: e.target.value})}>
        <option>Sélectionner un patient</option>
      </select>
      <input 
        type="date" 
        onChange={(e) => setAppointment({...appointment, date: e.target.value})}
      />
      <input 
        type="time" 
        onChange={(e) => setAppointment({...appointment, time: e.target.value})}
      />
      <button type="submit">Créer RDV</button>
    </form>
  )
}
```

#### APRÈS (Django API avec créneaux disponibles)
```javascript
// components/AppointmentBooking.js
import React, { useState, useEffect } from 'react'
import { appointmentService } from '../services/appointmentService'
import { patientService } from '../services/patientService'
import { medicalService } from '../services/medicalService'

function AppointmentBooking() {
  const [appointment, setAppointment] = useState({
    patient: '',
    medecin: '',
    date_heure: '',
    motif: ''
  })
  const [patients, setPatients] = useState([])
  const [medecins, setMedecins] = useState([])
  const [creneauxDisponibles, setCreneauxDisponibles] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      const [patientsData, medecinsData] = await Promise.all([
        patientService.getPatients(),
        medicalService.getMedecins()
      ])
      setPatients(patientsData.results)
      setMedecins(medecinsData.results)
    } catch (error) {
      console.error('Erreur chargement données:', error)
    }
  }

  const loadCreneauxDisponibles = async (medecinId, date) => {
    if (!medecinId || !date) return
    
    try {
      const creneaux = await appointmentService.getCreneauxDisponibles(medecinId, date)
      setCreneauxDisponibles(creneaux)
    } catch (error) {
      console.error('Erreur créneaux:', error)
    }
  }

  const handleMedecinChange = (medecinId) => {
    setAppointment({...appointment, medecin: medecinId})
    if (appointment.date_heure) {
      const date = appointment.date_heure.split('T')[0]
      loadCreneauxDisponibles(medecinId, date)
    }
  }

  const handleDateChange = (date) => {
    setAppointment({...appointment, date_heure: date})
    if (appointment.medecin) {
      loadCreneauxDisponibles(appointment.medecin, date.split('T')[0])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await appointmentService.createRendezVous(appointment)
      alert('Rendez-vous créé avec succès!')
      // Reset form
      setAppointment({ patient: '', medecin: '', date_heure: '', motif: '' })
      setCreneauxDisponibles([])
    } catch (error) {
      alert('Erreur lors de la création du rendez-vous')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Nouveau Rendez-vous</h2>

      <select 
        value={appointment.patient}
        onChange={(e) => setAppointment({...appointment, patient: e.target.value})}
        required
      >
        <option value="">Sélectionner un patient</option>
        {patients.map(patient => (
          <option key={patient.id} value={patient.id}>
            {patient.nom} {patient.prenom}
          </option>
        ))}
      </select>

      <select 
        value={appointment.medecin}
        onChange={(e) => handleMedecinChange(e.target.value)}
        required
      >
        <option value="">Sélectionner un médecin</option>
        {medecins.map(medecin => (
          <option key={medecin.id} value={medecin.id}>
            Dr. {medecin.nom} {medecin.prenom} - {medecin.specialite?.nom}
          </option>
        ))}
      </select>

      <input 
        type="date" 
        value={appointment.date_heure.split('T')[0] || ''}
        onChange={(e) => handleDateChange(e.target.value)}
        min={new Date().toISOString().split('T')[0]}
        required
      />

      {creneauxDisponibles.length > 0 && (
        <select 
          value={appointment.date_heure}
          onChange={(e) => setAppointment({...appointment, date_heure: e.target.value})}
          required
        >
          <option value="">Sélectionner un créneau</option>
          {creneauxDisponibles.map(creneau => (
            <option key={creneau} value={creneau}>
              {new Date(creneau).toLocaleTimeString('fr-FR', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </option>
          ))}
        </select>
      )}

      <textarea 
        placeholder="Motif de la consultation"
        value={appointment.motif}
        onChange={(e) => setAppointment({...appointment, motif: e.target.value})}
        required
      />

      <button type="submit" disabled={loading || !appointment.date_heure}>
        {loading ? 'Création...' : 'Créer Rendez-vous'}
      </button>
    </form>
  )
}
```

### 4. **Dashboard Component avec Statistiques**

#### NOUVEAU (Django API)
```javascript
// components/Dashboard.js
import React, { useState, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'
import { patientService } from '../services/patientService'
import { appointmentService } from '../services/appointmentService'
import { medicalService } from '../services/medicalService'

function Dashboard() {
  const [stats, setStats] = useState({
    patients: { total: 0, nouveaux: 0 },
    rdv: { aujourdhui: 0, semaine: 0 },
    consultations: { total: 0, mois: 0 }
  })
  const [loading, setLoading] = useState(true)
  const { state } = useApp()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [patientsStats, rdvStats, consultationsStats] = await Promise.all([
        patientService.getStatistiques(),
        appointmentService.getStatistiques(),
        medicalService.getStatistiques()
      ])

      setStats({
        patients: patientsStats,
        rdv: rdvStats,
        consultations: consultationsStats
      })
    } catch (error) {
      console.error('Erreur chargement dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Chargement du tableau de bord...</div>

  return (
    <div className="dashboard">
      <h1>Tableau de Bord - {state.user?.hopital?.nom}</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Patients</h3>
          <div className="stat-number">{stats.patients.total}</div>
          <div className="stat-detail">+{stats.patients.nouveaux} ce mois</div>
        </div>

        <div className="stat-card">
          <h3>Rendez-vous</h3>
          <div className="stat-number">{stats.rdv.aujourdhui}</div>
          <div className="stat-detail">Aujourd'hui</div>
        </div>

        <div className="stat-card">
          <h3>Consultations</h3>
          <div className="stat-number">{stats.consultations.mois}</div>
          <div className="stat-detail">Ce mois</div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Actions Rapides</h2>
        <button onClick={() => window.location.href = '/patients/new'}>
          Nouveau Patient
        </button>
        <button onClick={() => window.location.href = '/appointments/new'}>
          Nouveau RDV
        </button>
        <button onClick={() => window.location.href = '/consultations/new'}>
          Nouvelle Consultation
        </button>
      </div>
    </div>
  )
}
```

### 5. **Error Boundary Component**

```javascript
// components/ErrorBoundary.js
import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Oops! Une erreur s'est produite</h2>
          <p>Veuillez rafraîchir la page ou contacter le support.</p>
          <button onClick={() => window.location.reload()}>
            Rafraîchir
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
```

## 🎯 Points Clés de Migration

### 1. **Gestion des États**
- Utiliser Context API ou Redux pour l'état global
- Gérer loading states pour toutes les requêtes
- Implémenter error handling robuste

### 2. **Authentification**
- JWT tokens avec auto-refresh
- Redirection automatique si non authentifié
- Gestion des permissions par rôle

### 3. **Performance**
- Pagination sur toutes les listes
- Lazy loading des composants
- Cache des données fréquemment utilisées

### 4. **UX/UI**
- Loading spinners
- Messages d'erreur clairs
- Confirmations pour actions critiques
- Feedback utilisateur immédiat

---

Ces exemples montrent la transformation complète de votre frontend React pour s'adapter au nouveau backend Django avec toutes ses fonctionnalités avancées.