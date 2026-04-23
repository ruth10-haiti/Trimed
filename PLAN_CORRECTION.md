# Plan d'Action - Correction des Problèmes Critiques

## 🎯 Objectif
Transformer le projet Trimed Backend d'un état incomplet (20% fonctionnel) vers un état production-ready (100% fonctionnel).

## 📊 État Actuel vs Cible

| Composant | État Actuel | Cible | Priorité |
|-----------|-------------|-------|----------|
| URLs/Endpoints | 20% | 100% | 🔴 Critique |
| ViewSets | 15% | 100% | 🔴 Critique |
| Serializers | 25% | 100% | 🔴 Critique |
| Permissions | 30% | 100% | 🟡 Haute |
| Tests | 0% | 80% | 🟡 Haute |
| Documentation | 10% | 90% | 🟢 Moyenne |

## 🚀 Phase 1: Fondations (Semaine 1-2)

### 1.1 Créer tous les Serializers manquants

#### Patients Module
```python
# patients/serializers.py - À créer
- PatientSerializer ✅ (existe)
- PatientListSerializer ❌ (manque)
- AdressePatientSerializer ❌ (manque)
- PersonneAContacterSerializer ❌ (manque)
- AssurancePatientSerializer ❌ (manque)
- AllergiePatientSerializer ❌ (manque)
- AntecedentMedicalSerializer ❌ (manque)
- SuiviPatientSerializer ❌ (manque)
```

#### Medical Module
```python
# medical/serializers.py - À créer entièrement
- MedecinSerializer
- SpecialiteSerializer
- GroupeSanguinSerializer
- ConsultationSerializer
- OrdonnanceSerializer
- ExamenMedicalSerializer
- PrescriptionSerializer
```

#### Autres Modules
```python
# rendez_vous/serializers.py - À créer
# gestion_medicaments/serializers.py - À créer
# facturation/serializers.py - À créer
# notifications/serializers.py - À créer
# gestion_tenants/serializers.py - À créer
```

### 1.2 Implémenter tous les ViewSets

#### Structure type pour chaque ViewSet:
```python
class ExempleViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        # Filtrage par tenant
        return super().get_queryset().filter(tenant=self.request.user.hopital)
    
    def get_permissions(self):
        # Permissions par action
        pass
```

### 1.3 Compléter toutes les URLs

#### Exemple pour chaque module:
```python
# patients/urls.py
router.register(r'patients', PatientViewSet)
router.register(r'adresses', AdressePatientViewSet)
router.register(r'allergies', AllergiePatientViewSet)
# ... etc
```

## 🔧 Phase 2: Fonctionnalités Core (Semaine 3-4)

### 2.1 Système de Permissions Complet

#### Créer permissions personnalisées:
```python
# comptes/permissions.py - À étendre
class PeutVoirPatients(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['medecin', 'infirmier', 'secretaire']

class PeutModifierPatients(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['medecin', 'infirmier']
```

#### Matrice des permissions par rôle:
| Rôle | Patients | Consultations | Médicaments | Rendez-vous | Facturation |
|------|----------|---------------|-------------|-------------|-------------|
| admin-systeme | CRUD | CRUD | CRUD | CRUD | CRUD |
| proprietaire-hopital | CRUD | R | CRUD | CRUD | CRUD |
| medecin | CRUD | CRUD | R | CRUD | R |
| infirmier | RU | R | R | R | - |
| secretaire | R | R | R | CRUD | R |
| patient | R (soi) | R (soi) | - | R (soi) | R (soi) |

### 2.2 Endpoints Critiques à Implémenter

#### Patients (`/api/patients/`)
```
GET    /                     # Liste patients
POST   /                     # Créer patient
GET    /{id}/                # Détail patient
PUT    /{id}/                # Modifier patient
DELETE /{id}/                # Supprimer patient
GET    /{id}/dossier-complet/ # Dossier médical complet
POST   /{id}/allergies/      # Ajouter allergie
POST   /{id}/antecedents/    # Ajouter antécédent
GET    /{id}/statistiques/   # Stats patient
```

#### Médical (`/api/medical/`)
```
GET    /medecins/            # Liste médecins
POST   /medecins/            # Créer médecin
GET    /consultations/       # Liste consultations
POST   /consultations/       # Créer consultation
GET    /consultations/{id}/  # Détail consultation
POST   /consultations/{id}/ordonnances/ # Créer ordonnance
GET    /examens/             # Liste examens
POST   /examens/             # Créer examen
```

#### Rendez-vous (`/api/rendez-vous/`)
```
GET    /                     # Liste RDV
POST   /                     # Créer RDV
GET    /{id}/                # Détail RDV
PUT    /{id}/                # Modifier RDV
DELETE /{id}/                # Annuler RDV
GET    /creneaux-disponibles/ # Créneaux libres
POST   /{id}/confirmer/      # Confirmer RDV
POST   /{id}/reporter/       # Reporter RDV
```

#### Médicaments (`/api/medicaments/`)
```
GET    /                     # Liste médicaments
POST   /                     # Ajouter médicament
PUT    /{id}/                # Modifier médicament
POST   /{id}/stock/          # Mettre à jour stock
GET    /categories/          # Catégories
GET    /stock-faible/        # Médicaments en rupture
```

## 🧪 Phase 3: Tests et Validation (Semaine 5)

### 3.1 Tests Unitaires par Module

#### Structure des tests:
```python
# tests/test_patients.py
class PatientViewSetTest(APITestCase):
    def setUp(self):
        # Créer utilisateurs test
        # Créer tenant test
        # Créer patients test
    
    def test_list_patients_medecin(self):
        # Test liste pour médecin
    
    def test_create_patient_permissions(self):
        # Test permissions création
    
    def test_patient_dossier_complet(self):
        # Test dossier complet
```

### 3.2 Tests d'Intégration

#### Scénarios critiques:
1. **Parcours patient complet**: Inscription → RDV → Consultation → Ordonnance
2. **Gestion multi-tenant**: Isolation des données par hôpital
3. **Permissions par rôle**: Vérifier accès selon le rôle
4. **API Authentication**: JWT flow complet

## 📚 Phase 4: Documentation (Semaine 6)

### 4.1 Documentation API Swagger
- Descriptions détaillées pour chaque endpoint
- Exemples de requêtes/réponses
- Codes d'erreur documentés
- Schémas de données complets

### 4.2 Guide d'Intégration Frontend
```json
{
  "authentication": {
    "login": "POST /api/comptes/login/",
    "refresh": "POST /api/comptes/token/refresh/",
    "logout": "POST /api/comptes/logout/"
  },
  "patients": {
    "list": "GET /api/patients/",
    "create": "POST /api/patients/",
    "detail": "GET /api/patients/{id}/"
  }
}
```

## 🎯 Livrables par Phase

### Phase 1 (Semaines 1-2)
- [ ] 8 modules avec serializers complets
- [ ] 8 modules avec ViewSets fonctionnels
- [ ] 8 modules avec URLs configurées
- [ ] Tests de base pour authentification

### Phase 2 (Semaines 3-4)
- [ ] Système de permissions complet
- [ ] 50+ endpoints REST fonctionnels
- [ ] Validation des données d'entrée
- [ ] Gestion d'erreurs standardisée

### Phase 3 (Semaine 5)
- [ ] 100+ tests unitaires
- [ ] 20+ tests d'intégration
- [ ] Coverage > 80%
- [ ] Tests de performance

### Phase 4 (Semaine 6)
- [ ] Documentation Swagger complète
- [ ] Guide d'intégration frontend
- [ ] Guide de déploiement
- [ ] Exemples d'utilisation

## 📈 Métriques de Succès

| Métrique | Avant | Cible | Mesure |
|----------|-------|-------|---------|
| Endpoints fonctionnels | 5 | 50+ | Swagger UI |
| Coverage tests | 0% | 80%+ | pytest-cov |
| Temps réponse API | N/A | <200ms | Tests perf |
| Documentation | 10% | 90% | Swagger completeness |

## 🚨 Risques et Mitigation

### Risques Identifiés
1. **Complexité multi-tenant**: Isolation des données
2. **Permissions complexes**: Matrice rôles/actions
3. **Performance**: Requêtes N+1
4. **Sécurité**: Validation des entrées

### Stratégies de Mitigation
1. **Tests rigoureux** pour chaque tenant
2. **Permissions centralisées** dans un module dédié
3. **Optimisation ORM** avec select_related/prefetch_related
4. **Validation stricte** avec serializers DRF

## 💡 Recommandations Techniques

### Architecture
- Utiliser des **ViewSets génériques** pour réduire la duplication
- Implémenter des **mixins** pour les fonctionnalités communes
- Centraliser la **gestion des permissions**
- Standardiser les **réponses d'erreur**

### Performance
- Ajouter **pagination** sur toutes les listes
- Implémenter **cache Redis** pour les données fréquentes
- Optimiser les **requêtes ORM**
- Ajouter **monitoring** des performances

### Sécurité
- Valider **toutes les entrées** utilisateur
- Implémenter **rate limiting**
- Ajouter **audit trail** pour les actions critiques
- Sécuriser les **uploads de fichiers**

---

**Estimation totale**: 6 semaines développeur senior
**Budget estimé**: 30-40 jours/homme
**ROI**: Projet production-ready vs prototype actuel