from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Medecin, Specialite, GroupeSanguin, Consultation,
    Ordonnance, ExamenMedical, Prescription
)
from .serializers import (
    MedecinSerializer, MedecinListSerializer, SpecialiteSerializer,
    GroupeSanguinSerializer, ConsultationSerializer, ConsultationListSerializer,
    ConsultationCreateSerializer, OrdonnanceSerializer, OrdonnanceListSerializer,
    OrdonnanceCreateSerializer, ExamenMedicalSerializer, ExamenMedicalListSerializer,
    PrescriptionSerializer
)
from comptes.permissions import (
    EstMedecin, EstPersonnel, EstPatient, 
    EstProprietaireHopital, EstAdminSysteme
)


class SpecialiteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les spécialités médicales"""
    queryset = Specialite.objects.all()
    serializer_class = SpecialiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nom_specialite', 'description']
    filterset_fields = ['actif']
    
    def get_queryset(self):
        """Vérifier Swagger et authentification"""
        if getattr(self, 'swagger_fake_view', False):
            return Specialite.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return Specialite.objects.none()
        
        # Filtrer par tenant si nécessaire
        if hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(hopital=user.hopital)
        
        return queryset


class GroupeSanguinViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les groupes sanguins (lecture seule)"""
    queryset = GroupeSanguin.objects.all()
    serializer_class = GroupeSanguinSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return GroupeSanguin.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return GroupeSanguin.objects.none()
        
        return queryset


class MedecinViewSet(viewsets.ModelViewSet):
    """ViewSet pour les médecins"""
    queryset = Medecin.objects.all().order_by('-cree_le')
    serializer_class = MedecinSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialite_principale', 'sexe']
    search_fields = ['nom', 'prenom', 'email_professionnel', 'numero_matricule_professionnel']
    ordering_fields = ['nom', 'prenom', 'cree_le']
    ordering = ['nom', 'prenom']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MedecinListSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        CORRECTION: Permissions pour les médecins
        """
        if self.action == 'list':
            # Tout utilisateur authentifié peut voir la liste
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            # Tout utilisateur authentifié peut voir un médecin
            permission_classes = [IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Seuls les admins système, propriétaires, personnel et médecins peuvent modifier
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital | EstPersonnel | EstMedecin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        CORRECTION: Filtrer les médecins selon les permissions avec vérification Swagger
        """
        if getattr(self, 'swagger_fake_view', False):
            return Medecin.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return Medecin.objects.none()
        
        # Admin système voit tout
        if hasattr(user, 'role') and user.role == 'admin-systeme':
            return queryset
        
        # Propriétaire voit les médecins de son hôpital
        if hasattr(user, 'role') and user.role == 'proprietaire-hopital':
            if hasattr(user, 'hopital') and user.hopital:
                return queryset.filter(hopital=user.hopital)
            return Medecin.objects.none()
        
        # Personnel voit les médecins de son hôpital
        if hasattr(user, 'role') and user.role in ['personnel', 'secretaire', 'infirmier']:
            if hasattr(user, 'hopital') and user.hopital:
                return queryset.filter(hopital=user.hopital)
            return Medecin.objects.none()
        
        # Médecin voit son propre profil
        if hasattr(user, 'role') and user.role == 'medecin':
            if hasattr(user, 'medecin_lie'):
                return queryset.filter(pk=user.medecin_lie.pk)
            return Medecin.objects.none()
        
        # Patient voit les médecins de son hôpital
        if hasattr(user, 'role') and user.role == 'patient':
            if hasattr(user, 'hopital') and user.hopital:
                return queryset.filter(hopital=user.hopital)
            return Medecin.objects.none()
        
        # Par défaut, filtrer par hôpital
        if hasattr(user, 'hopital') and user.hopital:
            return queryset.filter(hopital=user.hopital)
        
        return queryset.select_related('specialite_principale', 'utilisateur')
    
    def perform_create(self, serializer):
        """Surcharge pour ajouter automatiquement le tenant"""
        user = self.request.user
        
        if hasattr(user, 'hopital') and user.hopital:
            serializer.save(
                hopital=user.hopital,
                cree_par_utilisateur=user
            )
        else:
            serializer.save(cree_par_utilisateur=user)
    
    @action(detail=True, methods=['get'])
    def consultations(self, request, pk=None):
        """Récupérer les consultations d'un médecin"""
        medecin = self.get_object()
        consultations = Consultation.objects.filter(medecin=medecin).order_by('-date_consultation')
        
        # Filtrage par date
        date_debut = request.query_params.get('date_debut')
        date_fin = request.query_params.get('date_fin')
        
        if date_debut:
            try:
                date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
                consultations = consultations.filter(date_consultation__date__gte=date_debut)
            except ValueError:
                pass
        
        if date_fin:
            try:
                date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
                consultations = consultations.filter(date_consultation__date__lte=date_fin)
            except ValueError:
                pass
        
        page = self.paginate_queryset(consultations)
        if page is not None:
            serializer = ConsultationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ConsultationListSerializer(consultations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        """Statistiques d'un médecin"""
        medecin = self.get_object()
        
        # Consultations
        total_consultations = Consultation.objects.filter(medecin=medecin).count()
        consultations_mois = Consultation.objects.filter(
            medecin=medecin,
            date_consultation__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Ordonnances
        total_ordonnances = Ordonnance.objects.filter(medecin=medecin).count()
        
        # Examens prescrits
        total_examens = ExamenMedical.objects.filter(medecin_prescripteur=medecin).count()
        
        return Response({
            'consultations_total': total_consultations,
            'consultations_ce_mois': consultations_mois,
            'ordonnances_total': total_ordonnances,
            'examens_prescrits': total_examens
        })


class ConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les consultations"""
    queryset = Consultation.objects.all().order_by('-date_consultation')
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'medecin', 'rendez_vous']
    search_fields = ['patient__nom', 'patient__prenom', 'medecin__nom', 'motif', 'diagnostic_principal']
    ordering_fields = ['date_consultation', 'created_at']
    ordering = ['-date_consultation']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultationListSerializer
        elif self.action == 'create':
            return ConsultationCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        CORRECTION: Permettre aux patients de créer des consultations
        """
        if self.action == 'create':
            # Les médecins, le personnel ET les patients peuvent créer des consultations
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel | EstPatient]
        elif self.action in ['update', 'partial_update']:
            # Seuls les médecins et le personnel peuvent modifier
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel]
        elif self.action == 'destroy':
            # Seuls les médecins et le personnel peuvent supprimer
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Consultation.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return Consultation.objects.none()
        
        # Admin système voit tout
        if hasattr(user, 'role') and user.role == 'admin-systeme':
            return queryset
        
        # Filtrage par tenant
        if hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        else:
            return Consultation.objects.none()
        
        # Filtrage par rôle
        if hasattr(user, 'role') and user.role == 'patient' and hasattr(user, 'patient_lie'):
            queryset = queryset.filter(patient=user.patient_lie)
        elif hasattr(user, 'role') and user.role == 'medecin' and hasattr(user, 'medecin_lie'):
            queryset = queryset.filter(medecin=user.medecin_lie)
        elif hasattr(user, 'role') and user.role in ['personnel', 'secretaire', 'infirmier']:
            # Le personnel voit toutes les consultations de l'hôpital
            pass
        
        # Filtres par date
        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')
        
        if date_debut:
            try:
                date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
                queryset = queryset.filter(date_consultation__date__gte=date_debut)
            except ValueError:
                pass
        
        if date_fin:
            try:
                date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
                queryset = queryset.filter(date_consultation__date__lte=date_fin)
            except ValueError:
                pass
        
        return queryset.select_related('patient', 'medecin', 'rendez_vous')
    
    def perform_create(self, serializer):
        """
        CORRECTION: Ajouter automatiquement le tenant et valider les données
        """
        user = self.request.user
        
        # Déterminer le tenant
        if hasattr(user, 'hopital') and user.hopital:
            tenant = user.hopital
        else:
            # Essayer de récupérer le tenant depuis le patient ou le médecin
            patient = serializer.validated_data.get('patient')
            medecin = serializer.validated_data.get('medecin')
            
            if patient and hasattr(patient, 'hopital'):
                tenant = patient.hopital
            elif medecin and hasattr(medecin, 'hopital'):
                tenant = medecin.hopital
            else:
                tenant = None
        
        # Sauvegarder avec le tenant
        if tenant:
            serializer.save(tenant=tenant)
        else:
            serializer.save()
    
    def create(self, request, *args, **kwargs):
        """
        CORRECTION: Surcharge de create pour mieux gérer les erreurs
        """
        try:
            # Vérifier que l'utilisateur est authentifié
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentification requise'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Vérifier les données requises
            required_fields = ['patient', 'medecin', 'date_consultation']
            missing_fields = [field for field in required_fields if field not in request.data]
            
            if missing_fields:
                return Response(
                    {'error': f'Champs manquants: {", ".join(missing_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Si c'est un patient qui crée, vérifier qu'il crée pour lui-même
            if hasattr(request.user, 'role') and request.user.role == 'patient':
                patient_id = request.data.get('patient')
                if hasattr(request.user, 'patient_lie'):
                    if str(request.user.patient_lie.patient_id) != str(patient_id):
                        return Response(
                            {'error': 'Vous ne pouvez créer une consultation que pour vous-même'},
                            status=status.HTTP_403_FORBIDDEN
                        )
            
            return super().create(request, *args, **kwargs)
            
        except Exception as e:
            # Loguer l'erreur pour le débogage
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la création de consultation: {str(e)}")
            
            return Response(
                {'error': f'Erreur lors de la création: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def creer_ordonnance(self, request, pk=None):
        """Créer une ordonnance pour cette consultation"""
        consultation = self.get_object()
        
        # Vérifier que l'utilisateur est authentifié
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentification requise'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Vérifier que l'utilisateur a le rôle médecin
        if not hasattr(request.user, 'role') or request.user.role != 'medecin':
            return Response(
                {'error': 'Seul un médecin peut créer une ordonnance'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le médecin correspond à celui de la consultation
        if not hasattr(request.user, 'medecin_lie'):
            return Response(
                {'error': 'Profil médecin non trouvé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.medecin_lie != consultation.medecin:
            return Response(
                {'error': 'Vous ne pouvez créer une ordonnance que pour vos propres consultations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Préparer les données
        ordonnance_data = request.data.copy()
        ordonnance_data['consultation'] = consultation.consultation_id
        ordonnance_data['patient'] = consultation.patient.patient_id
        ordonnance_data['medecin'] = consultation.medecin.medecin_id
        ordonnance_data['date_ordonnance'] = timezone.now()
        ordonnance_data['tenant'] = consultation.tenant.tenant_id if consultation.tenant else None
        
        serializer = OrdonnanceCreateSerializer(data=ordonnance_data, context={'request': request})
        if serializer.is_valid():
            ordonnance = serializer.save()
            return Response(OrdonnanceSerializer(ordonnance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def prescrire_examen(self, request, pk=None):
        """Prescrire un examen médical"""
        consultation = self.get_object()
        
        # Vérifier les permissions
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentification requise'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not hasattr(request.user, 'role') or request.user.role != 'medecin':
            return Response(
                {'error': 'Seuls les médecins peuvent prescrire des examens'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not hasattr(request.user, 'medecin_lie'):
            return Response(
                {'error': 'Profil médecin non trouvé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.user.medecin_lie != consultation.medecin:
            return Response(
                {'error': 'Vous ne pouvez prescrire des examens que pour vos propres consultations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Préparer les données
        examen_data = request.data.copy()
        examen_data['tenant'] = consultation.tenant.tenant_id if consultation.tenant else None
        examen_data['patient'] = consultation.patient.patient_id
        examen_data['consultation'] = consultation.consultation_id
        examen_data['medecin_prescripteur'] = consultation.medecin.medecin_id
        examen_data['date_examen'] = request.data.get('date_examen', timezone.now())
        
        serializer = ExamenMedicalSerializer(data=examen_data)
        if serializer.is_valid():
            examen = serializer.save()
            return Response(ExamenMedicalSerializer(examen).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrdonnanceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les ordonnances"""
    queryset = Ordonnance.objects.all().order_by('-date_ordonnance')
    serializer_class = OrdonnanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'medecin', 'consultation']
    search_fields = ['patient__nom', 'patient__prenom', 'medecin__nom', 'recommandations']
    ordering_fields = ['date_ordonnance', 'created_at']
    ordering = ['-date_ordonnance']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrdonnanceListSerializer
        elif self.action == 'create':
            return OrdonnanceCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Ordonnance.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return Ordonnance.objects.none()
        
        # Admin système voit tout
        if hasattr(user, 'role') and user.role == 'admin-systeme':
            return queryset
        
        # Filtrage par tenant
        if hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        else:
            return Ordonnance.objects.none()
        
        # Filtrage par rôle
        if hasattr(user, 'role') and user.role == 'patient' and hasattr(user, 'patient_lie'):
            queryset = queryset.filter(patient=user.patient_lie)
        elif hasattr(user, 'role') and user.role == 'medecin' and hasattr(user, 'medecin_lie'):
            queryset = queryset.filter(medecin=user.medecin_lie)
        
        return queryset.select_related('patient', 'medecin', 'consultation')
    
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'hopital') and user.hopital:
            serializer.save(tenant=user.hopital)
        else:
            serializer.save()


class ExamenMedicalViewSet(viewsets.ModelViewSet):
    """ViewSet pour les examens médicaux"""
    queryset = ExamenMedical.objects.all().order_by('-date_examen')
    serializer_class = ExamenMedicalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'consultation', 'medecin_prescripteur', 'type_examen']
    search_fields = ['patient__nom', 'patient__prenom', 'nom_examen', 'resultat']
    ordering_fields = ['date_examen', 'date_resultat', 'created_at']
    ordering = ['-date_examen']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExamenMedicalListSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, EstMedecin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ExamenMedical.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return ExamenMedical.objects.none()
        
        # Admin système voit tout
        if hasattr(user, 'role') and user.role == 'admin-systeme':
            return queryset
        
        # Filtrage par tenant
        if hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        else:
            return ExamenMedical.objects.none()
        
        # Filtrage par rôle
        if hasattr(user, 'role') and user.role == 'patient' and hasattr(user, 'patient_lie'):
            queryset = queryset.filter(patient=user.patient_lie)
        elif hasattr(user, 'role') and user.role == 'medecin' and hasattr(user, 'medecin_lie'):
            queryset = queryset.filter(medecin_prescripteur=user.medecin_lie)
        
        return queryset.select_related('patient', 'consultation', 'medecin_prescripteur')
    
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'hopital') and user.hopital:
            serializer.save(tenant=user.hopital)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def ajouter_resultat(self, request, pk=None):
        """Ajouter le résultat d'un examen"""
        examen = self.get_object()
        
        # Vérifier les permissions
        if not (hasattr(request.user, 'role') and request.user.role in ['medecin', 'infirmier', 'personnel']):
            return Response(
                {'error': 'Vous n\'avez pas la permission d\'ajouter des résultats'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        resultat = request.data.get('resultat')
        notes = request.data.get('notes', '')
        
        if not resultat:
            return Response(
                {'error': 'Le résultat est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        examen.resultat = resultat
        examen.notes = notes
        examen.date_resultat = timezone.now()
        examen.save()
        
        serializer = self.get_serializer(examen)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les prescriptions"""
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ordonnance', 'medicament']
    search_fields = ['medicament__nom', 'dosage', 'instructions']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Prescription.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return Prescription.objects.none()
        
        # Admin système voit tout
        if hasattr(user, 'role') and user.role == 'admin-systeme':
            return queryset
        
        # Filtrage par tenant via l'ordonnance
        if hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(ordonnance__tenant=user.hopital)
        else:
            return Prescription.objects.none()
        
        # Filtrage par rôle
        if hasattr(user, 'role') and user.role == 'patient' and hasattr(user, 'patient_lie'):
            queryset = queryset.filter(ordonnance__patient=user.patient_lie)
        elif hasattr(user, 'role') and user.role == 'medecin' and hasattr(user, 'medecin_lie'):
            queryset = queryset.filter(ordonnance__medecin=user.medecin_lie)
        
        return queryset.select_related('ordonnance', 'medicament')