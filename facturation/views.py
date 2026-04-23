# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import (
    Plan, Abonnement, Paiement, Invoice, Coupon, TarifConsultation,
    PaiementMethode, PaiementStatut
)
from .serializers import (
    PlanSerializer, AbonnementSerializer, PaiementSerializer,
    InvoiceSerializer, CouponSerializer, ValidationCouponSerializer,
    TarifConsultationSerializer
)
from comptes.permissions import EstAdminSysteme, EstProprietaireHopital

class AbonnementViewSet(viewsets.ModelViewSet):
    """ViewSet pour les abonnements"""
    queryset = Abonnement.objects.all()
    serializer_class = AbonnementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tenant', 'plan', 'statut']
    ordering_fields = ['date_debut', 'date_fin', 'created_at']
    
    def get_permissions(self):
        """
        Permissions personnalisées selon l'action
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, EstAdminSysteme]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins système voient tout
        if user.role == 'admin-systeme':
            return queryset
        
        # Propriétaires voient leur abonnement
        if user.role == 'proprietaire-hopital' and user.hopital:
            return queryset.filter(tenant=user.hopital)
        
        # Autres utilisateurs voient l'abonnement de leur tenant
        if user.hopital:
            return queryset.filter(tenant=user.hopital)
        
        return Abonnement.objects.none()
    
    @action(detail=True, methods=['post'])
    def renouveler(self, request, pk=None):
        """Renouveler un abonnement"""
        abonnement = self.get_object()
        
        # Vérifier que l'utilisateur est autorisé
        if not request.user.role in ['admin-systeme', 'proprietaire-hopital']:
            return Response(
                {'error': 'Vous n\'avez pas la permission de renouveler cet abonnement'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        periode_mois = request.data.get('periode_mois', 1)
        date_renouvellement = timezone.now()
        
        # Calculer la nouvelle date de fin
        if abonnement.date_fin < date_renouvellement.date():
            nouvelle_date_fin = date_renouvellement.date() + timedelta(days=30 * periode_mois)
        else:
            nouvelle_date_fin = abonnement.date_fin + timedelta(days=30 * periode_mois)
        
        # Mettre à jour l'abonnement
        abonnement.date_fin = nouvelle_date_fin
        abonnement.save()
        
        # Créer un paiement pour le renouvellement
        montant = abonnement.plan.prix_mensuel * periode_mois
        
        paiement = Paiement.objects.create(
            tenant=abonnement.tenant,
            abonnement=abonnement,
            methode=PaiementMethode.objects.get(nom='Carte bancaire'),
            statut=PaiementStatut.objects.get(nom='payé'),
            montant=montant,
            date_paiement=date_renouvellement,
            reference=f"RENOUV_{abonnement.tenant.tenant_id}_{date_renouvellement.strftime('%Y%m%d')}"
        )
        
        return Response({
            'message': 'Abonnement renouvelé avec succès',
            'ancienne_date_fin': abonnement.date_fin - timedelta(days=30 * periode_mois),
            'nouvelle_date_fin': abonnement.date_fin,
            'paiement': PaiementSerializer(paiement).data
        })
    
    @action(detail=False, methods=['get'])
    def abonnements_expirant(self, request):
        """Liste des abonnements expirant bientôt"""
        jours = int(request.query_params.get('jours', 30))
        
        date_limite = timezone.now().date() + timedelta(days=jours)
        queryset = self.get_queryset().filter(
            date_fin__lte=date_limite,
            date_fin__gte=timezone.now().date()
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'date_limite': date_limite,
            'jours': jours,
            'abonnements': serializer.data,
            'total': queryset.count()
        })

class PaiementViewSet(viewsets.ModelViewSet):
    """ViewSet pour les paiements"""
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tenant', 'methode', 'statut']
    ordering_fields = ['date_paiement', 'montant', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins système voient tout
        if user.role == 'admin-systeme':
            return queryset
        
        # Propriétaires voient leurs paiements
        if user.role == 'proprietaire-hopital' and user.hopital:
            return queryset.filter(tenant=user.hopital)
        
        return Paiement.objects.none()
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques des paiements"""
        user = request.user
        
        if user.role == 'admin-systeme':
            queryset = Paiement.objects.all()
        elif user.hopital:
            queryset = Paiement.objects.filter(tenant=user.hopital)
        else:
            return Response(
                {'error': 'Aucun tenant associé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Paiements du mois
        debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        paiements_mois = queryset.filter(date_paiement__gte=debut_mois)
        
        # Paiements de l'année
        debut_annee = debut_mois.replace(month=1)
        paiements_annee = queryset.filter(date_paiement__gte=debut_annee)
        
        data = {
            'total_paiements': queryset.count(),
            'montant_total': float(queryset.aggregate(models.Sum('montant'))['montant__sum'] or 0),
            'paiements_mois': paiements_mois.count(),
            'montant_mois': float(paiements_mois.aggregate(models.Sum('montant'))['montant__sum'] or 0),
            'paiements_annee': paiements_annee.count(),
            'montant_annee': float(paiements_annee.aggregate(models.Sum('montant'))['montant__sum'] or 0),
            'par_methode': list(queryset.values('methode__nom').annotate(
                total=models.Count('paiement_id'),
                montant=models.Sum('montant')
            )),
            'par_statut': list(queryset.values('statut__nom').annotate(
                total=models.Count('paiement_id'),
                montant=models.Sum('montant')
            )),
        }
        
        return Response(data)

class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet pour les coupons"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated, EstAdminSysteme]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'description']
    ordering_fields = ['date_debut', 'date_fin', 'created_at']
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def valider(self, request):
        """Valider un coupon"""
        serializer = ValidationCouponSerializer(data=request.data)
        
        if serializer.is_valid():
            coupon = serializer.validated_data['coupon']
            
            return Response({
                'valide': True,
                'coupon': CouponSerializer(coupon).data,
                'montant_initial': serializer.validated_data['montant_initial'],
                'montant_final': serializer.validated_data['montant_final'],
                'reduction': serializer.validated_data['reduction'],
                'message': 'Coupon valide'
            })
        
        return Response({
            'valide': False,
            'erreurs': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class TarifConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les tarifs de consultation"""
    queryset = TarifConsultation.objects.all()
    serializer_class = TarifConsultationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tenant', 'specialite', 'actif']
    ordering_fields = ['tarif_normal', 'date_debut']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtrer par tenant
        if user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        
        # Filtrer par date de validité
        date_reference = self.request.query_params.get('date_reference')
        if date_reference:
            try:
                date_ref = timezone.datetime.strptime(date_reference, '%Y-%m-%d').date()
            except ValueError:
                date_ref = timezone.now().date()
        else:
            date_ref = timezone.now().date()
        
        queryset = queryset.filter(
            date_debut__lte=date_ref
        ).filter(
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=date_ref)
        )
        
        return queryset
    
    def perform_create(self, serializer):
        """Surcharge pour ajouter automatiquement le tenant"""
        serializer.save(tenant=self.request.user.hopital)
    
    @action(detail=False, methods=['get'])
    def calculer_tarif(self, request):
        """Calculer un tarif de consultation"""
        specialite_id = request.query_params.get('specialite_id')
        est_urgence = request.query_params.get('urgence', 'false') == 'true'
        est_nuit = request.query_params.get('nuit', 'false') == 'true'
        est_weekend = request.query_params.get('weekend', 'false') == 'true'
        
        if not specialite_id:
            return Response(
                {'error': 'specialite_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tarif = TarifConsultation.objects.filter(
                tenant=request.user.hopital,
                specialite_id=specialite_id,
                actif=True,
                date_debut__lte=timezone.now().date()
            ).filter(
                models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=timezone.now().date())
            ).first()
            
            if not tarif:
                raise TarifConsultation.DoesNotExist()
            
            montant = tarif.get_tarif(est_urgence, est_nuit, est_weekend)
            
            return Response({
                'tarif': TarifConsultationSerializer(tarif).data,
                'conditions': {
                    'urgence': est_urgence,
                    'nuit': est_nuit,
                    'weekend': est_weekend
                },
                'montant': montant,
                'duree': tarif.duree_consultation
            })
        
        except TarifConsultation.DoesNotExist:
            return Response(
                {'error': 'Aucun tarif trouvé pour cette spécialité'},
                status=status.HTTP_404_NOT_FOUND
            )