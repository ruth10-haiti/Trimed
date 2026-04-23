from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Tenant, ParametreHopital
from .serializers import TenantSerializer, ParametreHopitalSerializer
from comptes.permissions import EstAdminSysteme, EstProprietaireHopital

class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des tenants
    """
    queryset = Tenant.objects.all().order_by('-cree_le')
    serializer_class = TenantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'email_professionnel', 'directeur']
    ordering_fields = ['nom', 'cree_le', 'nombre_de_lits']
    
    def get_permissions(self):
        """
        Permissions personnalisées selon l'action
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Seul l'admin système peut modifier
            permission_classes = [IsAuthenticated, EstAdminSysteme]
        elif self.action == 'retrieve':
            # Les détails d'un hôpital nécessitent une authentification
            permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            # La liste des hôpitaux est publique
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filtrer les tenants selon les permissions
        """
        # Éviter les erreurs lors de la génération Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Tenant.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        # Pour la liste publique, retourner tous les tenants actifs
        if self.action == 'list':
            return queryset.filter(statut='actif')
        
        # Pour les autres actions, l'utilisateur doit être authentifié
        if not user.is_authenticated:
            return Tenant.objects.none()
        
        # Admin système voit tout
        if hasattr(user, 'role') and user.role == 'admin-systeme':
            return queryset
        
        # Les propriétaires ne voient que leur tenant
        if hasattr(user, 'role') and user.role == 'proprietaire-hopital':
            return queryset.filter(proprietaire_utilisateur=user)
        
        # Les autres utilisateurs voient leur tenant
        if hasattr(user, 'hopital') and user.hopital:
            return queryset.filter(pk=user.hopital.pk)
        
        # Par défaut, retourner vide
        return Tenant.objects.none()
    
    @action(detail=True, methods=['patch'])
    def verifier_documents(self, request, pk=None):
        """Vérifier les documents d'un tenant"""
        tenant = self.get_object()
        action = request.data.get('action')
        commentaire = request.data.get('commentaire', '')
        
        if action == 'approuver':
            tenant.statut_verification_document = 'verifie'
            tenant.verifie_par = request.user
            tenant.date_verification = timezone.now()
            tenant.save()
            
            return Response({
                'status': 'success',
                'message': 'Documents approuvés avec succès'
            })
        
        elif action == 'rejeter':
            tenant.statut_verification_document = 'rejete'
            tenant.save()
            
            return Response({
                'status': 'success',
                'message': 'Documents rejetés',
                'commentaire': commentaire
            })
        
        return Response(
            {'error': 'Action invalide. Utilisez "approuver" ou "rejeter".'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        """Statistiques d'un tenant"""
        tenant = self.get_object()
        
        # Imports à l'intérieur pour éviter les imports circulaires
        from comptes.models import Utilisateur
        from patients.models import Patient
        from medical.models import Medecin, Consultation
        from rendez_vous.models import RendezVous
        
        data = {
            'utilisateurs': Utilisateur.objects.filter(hopital=tenant).count(),
            'patients': Patient.objects.filter(hopital=tenant).count(),
            'medecins': Medecin.objects.filter(hopital=tenant).count(),
            'consultations_mois': Consultation.objects.filter(
                tenant=tenant,
                date_consultation__month=timezone.now().month
            ).count(),
            'rdv_a_venir': RendezVous.objects.filter(
                tenant=tenant,
                date_heure__gte=timezone.now()
            ).count(),
        }
        
        return Response(data)


class ParametreHopitalViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des paramètres d'hôpital
    """
    queryset = ParametreHopital.objects.all()
    serializer_class = ParametreHopitalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        CORRECTION: Filtrer par tenant de l'utilisateur avec vérification Swagger
        """
        # CORRECTION: Vérifier si c'est pour la génération Swagger
        if getattr(self, 'swagger_fake_view', False):
            return ParametreHopital.objects.none()
        
        queryset = super().get_queryset()
        user = self.request.user
        
        # Vérifier si l'utilisateur est authentifié
        if not user.is_authenticated:
            return ParametreHopital.objects.none()
        
        # CORRECTION: Utiliser hasattr pour éviter AttributeError
        if hasattr(user, 'role') and user.role == 'admin-systeme':
            return queryset
        
        if hasattr(user, 'hopital') and user.hopital:
            return queryset.filter(tenant=user.hopital)
        
        return ParametreHopital.objects.none()