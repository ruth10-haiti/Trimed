# rendez_vous/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import RendezVous, RendezVousType, RendezVousStatut
from .serializers import (
    RendezVousSerializer, RendezVousListSerializer, RendezVousCreateSerializer,
    RendezVousTypeSerializer, RendezVousStatutSerializer, CreneauDisponibleSerializer
)
from comptes.permissions import EstMedecin, EstPersonnel, EstPatient, EstAdminSysteme, EstProprietaireHopital


class RendezVousTypeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les types de rendez-vous"""
    serializer_class = RendezVousTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nom', 'description']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital | EstMedecin | EstPersonnel]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = RendezVousType.objects.all()
        user = self.request.user
        
        if user.is_authenticated and hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        elif user.is_authenticated:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'hopital') or not self.request.user.hopital:
            raise serializers.ValidationError("Aucun hôpital associé à cet utilisateur")
        serializer.save(tenant=self.request.user.hopital)


class RendezVousStatutViewSet(viewsets.ModelViewSet):
    """ViewSet pour les statuts de rendez-vous"""
    serializer_class = RendezVousStatutSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nom', 'description']
    filterset_fields = ['est_annule', 'est_confirme', 'est_termine']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital | EstMedecin | EstPersonnel]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = RendezVousStatut.objects.all()
        user = self.request.user
        
        if user.is_authenticated and hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        elif user.is_authenticated:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'hopital') or not self.request.user.hopital:
            raise serializers.ValidationError("Aucun hôpital associé à cet utilisateur")
        serializer.save(tenant=self.request.user.hopital)


class RendezVousViewSet(viewsets.ModelViewSet):
    """ViewSet pour les rendez-vous"""
    queryset = RendezVous.objects.all()
    serializer_class = RendezVousSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'medecin', 'type', 'statut']
    search_fields = ['patient__nom', 'patient__prenom', 'medecin__nom', 'medecin__prenom', 'motif']
    ordering_fields = ['date_heure', 'created_at']
    ordering = ['date_heure']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RendezVousListSerializer
        elif self.action == 'create':
            return RendezVousCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Permissions personnalisées selon l'action
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, EstPatient | EstMedecin | EstPersonnel]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, EstPatient | EstMedecin | EstPersonnel]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital | EstMedecin | EstPersonnel]
        elif self.action in ['confirmer', 'annuler', 'reporter']:
            permission_classes = [IsAuthenticated, EstPatient | EstMedecin | EstPersonnel]
        elif self.action == 'rendez_vous_patient':
            permission_classes = [IsAuthenticated, EstMedecin | EstPersonnel | EstAdminSysteme | EstProprietaireHopital]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_authenticated and hasattr(user, 'hopital') and user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        
        if user.is_authenticated:
            if user.role == 'patient' and hasattr(user, 'patient'):
                queryset = queryset.filter(patient=user.patient)
            elif user.role == 'medecin' and hasattr(user, 'medecin'):
                queryset = queryset.filter(medecin=user.medecin)
        
        date_debut = self.request.query_params.get('date_debut', None)
        date_fin = self.request.query_params.get('date_fin', None)
        
        if date_debut:
            try:
                date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
                queryset = queryset.filter(date_heure__date__gte=date_debut)
            except ValueError:
                pass
        
        if date_fin:
            try:
                date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
                queryset = queryset.filter(date_heure__date__lte=date_fin)
            except ValueError:
                pass
        
        if self.request.query_params.get('aujourdhui', None) == 'true':
            aujourd_hui = timezone.now().date()
            queryset = queryset.filter(date_heure__date=aujourd_hui)
        
        if self.request.query_params.get('cette_semaine', None) == 'true':
            aujourd_hui = timezone.now().date()
            debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
            fin_semaine = debut_semaine + timedelta(days=6)
            queryset = queryset.filter(
                date_heure__date__gte=debut_semaine,
                date_heure__date__lte=fin_semaine
            )
        
        return queryset.select_related('patient', 'medecin', 'type', 'statut')
    
    def perform_create(self, serializer):
        user = self.request.user
        
        if user.role == 'patient' and hasattr(user, 'patient'):
            serializer.save(tenant=user.hopital, patient=user.patient)
        else:
            serializer.save(tenant=user.hopital)
    
    def create(self, request, *args, **kwargs):
        print("=" * 50)
        print("📝 Données reçues pour création rendez-vous:")
        print(f"   User: {request.user} (role: {request.user.role if hasattr(request.user, 'role') else 'N/A'})")
        print(f"   Data: {request.data}")
        print("=" * 50)
        
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"❌ Erreur lors de la création: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mes_rendez_vous(self, request):
        """Récupérer les rendez-vous de l'utilisateur connecté"""
        user = request.user
        
        if user.role == 'patient' and hasattr(user, 'patient'):
            queryset = RendezVous.objects.filter(patient=user.patient)
        elif user.role == 'medecin' and hasattr(user, 'medecin'):
            queryset = RendezVous.objects.filter(medecin=user.medecin)
        else:
            return Response(
                {'error': 'Vous n\'avez pas de rendez-vous associés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        statut = request.query_params.get('statut', None)
        if statut:
            queryset = queryset.filter(statut__nom__iexact=statut)
        
        date = request.query_params.get('date', None)
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date_heure__date=date_obj)
            except ValueError:
                pass
        
        serializer = RendezVousListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='patient/(?P<patient_id>[^/.]+)')
    def rendez_vous_patient(self, request, patient_id=None):
        """Récupérer tous les rendez-vous d'un patient spécifique"""
        print(f"📋 Récupération des rendez-vous pour le patient ID: {patient_id}")
        
        user = request.user
        
        if user.role == 'patient' and hasattr(user, 'patient'):
            if str(user.patient.id) != patient_id:
                return Response(
                    {'error': 'Vous ne pouvez voir que vos propres rendez-vous'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        queryset = self.get_queryset().filter(patient_id=patient_id)
        
        statut = request.query_params.get('statut', None)
        if statut:
            queryset = queryset.filter(statut__nom__iexact=statut)
        
        date = request.query_params.get('date', None)
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date_heure__date=date_obj)
            except ValueError:
                pass
        
        date_debut = request.query_params.get('date_debut', None)
        if date_debut:
            try:
                date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
                queryset = queryset.filter(date_heure__date__gte=date_debut_obj)
            except ValueError:
                pass
        
        date_fin = request.query_params.get('date_fin', None)
        if date_fin:
            try:
                date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
                queryset = queryset.filter(date_heure__date__lte=date_fin_obj)
            except ValueError:
                pass
        
        serializer = RendezVousListSerializer(queryset, many=True)
        
        print(f"✅ {queryset.count()} rendez-vous trouvés pour le patient {patient_id}")
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def creneaux_disponibles(self, request):
        """Récupérer les créneaux disponibles pour un médecin"""
        medecin_id = request.query_params.get('medecin_id')
        date_str = request.query_params.get('date')
        duree = int(request.query_params.get('duree', 30))
        
        if not medecin_id or not date_str:
            return Response(
                {'error': 'medecin_id et date sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date_rdv = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Format de date invalide (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if date_rdv < timezone.now().date():
            return Response(
                {'error': 'La date ne peut pas être dans le passé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if date_rdv.weekday() == 6:
            return Response(
                {'error': 'Pas de rendez-vous le dimanche'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rdv_existants = RendezVous.objects.filter(
            medecin_id=medecin_id,
            date_heure__date=date_rdv,
            statut__est_annule=False
        ).order_by('date_heure')
        
        creneaux = []
        heure_debut = time(8, 0)
        heure_fin = time(18, 0)
        
        current_time = datetime.combine(date_rdv, heure_debut)
        end_time = datetime.combine(date_rdv, heure_fin)
        
        while current_time + timedelta(minutes=duree) <= end_time:
            creneau_fin = current_time + timedelta(minutes=duree)
            
            est_libre = True
            for rdv in rdv_existants:
                rdv_fin = rdv.date_heure + timedelta(minutes=rdv.duree)
                if (current_time < rdv_fin and creneau_fin > rdv.date_heure):
                    est_libre = False
                    break
            
            creneaux.append({
                'date': date_rdv,
                'heure_debut': current_time.time(),
                'heure_fin': creneau_fin.time(),
                'disponible': est_libre,
                'duree': duree
            })
            
            current_time += timedelta(minutes=30)
        
        serializer = CreneauDisponibleSerializer(creneaux, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirmer(self, request, pk=None):
        """Confirmer un rendez-vous"""
        rdv = self.get_object()
        
        if request.user.role not in ['medecin', 'secretaire', 'infirmier', 'admin-systeme', 'proprietaire-hopital']:
            return Response(
                {'error': 'Vous n\'avez pas la permission de confirmer ce rendez-vous'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        statut_confirme, created = RendezVousStatut.objects.get_or_create(
            tenant=rdv.tenant,
            nom='Confirmé',
            defaults={
                'description': 'Rendez-vous confirmé',
                'couleur': '#2ecc71',
                'est_confirme': True
            }
        )
        
        rdv.statut = statut_confirme
        rdv.save()
        
        serializer = self.get_serializer(rdv)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annuler un rendez-vous"""
        rdv = self.get_object()
        
        user = request.user
        is_patient_owner = user.role == 'patient' and hasattr(user, 'patient') and user.patient == rdv.patient
        
        if not (is_patient_owner or user.role in ['medecin', 'secretaire', 'admin-systeme', 'proprietaire-hopital']):
            return Response(
                {'error': 'Vous n\'avez pas la permission d\'annuler ce rendez-vous'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        statut_annule, created = RendezVousStatut.objects.get_or_create(
            tenant=rdv.tenant,
            nom='Annulé',
            defaults={
                'description': 'Rendez-vous annulé',
                'couleur': '#e74c3c',
                'est_annule': True
            }
        )
        
        rdv.statut = statut_annule
        rdv.raison_annulation = request.data.get('raison', '')
        rdv.save()
        
        serializer = self.get_serializer(rdv)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reporter(self, request, pk=None):
        """Reporter un rendez-vous"""
        rdv = self.get_object()
        nouvelle_date = request.data.get('nouvelle_date_heure')
        
        if not nouvelle_date:
            return Response(
                {'error': 'nouvelle_date_heure est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        is_patient_owner = user.role == 'patient' and hasattr(user, 'patient') and user.patient == rdv.patient
        
        if not (is_patient_owner or user.role in ['medecin', 'secretaire', 'admin-systeme', 'proprietaire-hopital']):
            return Response(
                {'error': 'Vous n\'avez pas la permission de reporter ce rendez-vous'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            nouvelle_date = datetime.fromisoformat(nouvelle_date.replace('Z', '+00:00'))
        except ValueError:
            return Response(
                {'error': 'Format de date invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if nouvelle_date < timezone.now():
            return Response(
                {'error': 'La nouvelle date ne peut pas être dans le passé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conflits = RendezVous.objects.filter(
            medecin=rdv.medecin,
            date_heure__date=nouvelle_date.date(),
            statut__est_annule=False
        ).exclude(pk=rdv.pk)
        
        for conflit in conflits:
            conflit_fin = conflit.date_heure + timedelta(minutes=conflit.duree)
            rdv_fin = nouvelle_date + timedelta(minutes=rdv.duree)
            if nouvelle_date < conflit_fin and rdv_fin > conflit.date_heure:
                return Response(
                    {'error': 'Conflit avec un autre rendez-vous'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        rdv.date_heure = nouvelle_date
        rdv.save()
        
        serializer = self.get_serializer(rdv)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques des rendez-vous"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        aujourd_hui = queryset.filter(date_heure__date=timezone.now().date()).count()
        cette_semaine = queryset.filter(
            date_heure__date__gte=timezone.now().date() - timedelta(days=7)
        ).count()
        
        par_statut = {}
        for statut in RendezVousStatut.objects.filter(tenant=request.user.hopital):
            count = queryset.filter(statut=statut).count()
            par_statut[statut.nom] = count
        
        par_medecin = {}
        if request.user.role in ['admin-systeme', 'proprietaire-hopital']:
            from medical.models import Medecin
            for medecin in Medecin.objects.filter(hopital=request.user.hopital):
                count = queryset.filter(medecin=medecin).count()
                par_medecin[f"Dr {medecin.prenom} {medecin.nom}"] = count
        
        return Response({
            'total': total,
            'aujourd_hui': aujourd_hui,
            'cette_semaine': cette_semaine,
            'par_statut': par_statut,
            'par_medecin': par_medecin
        })