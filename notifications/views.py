# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from .models import Notification, NotificationType, PreferenceNotification
from .serializers import (
    NotificationSerializer, NotificationTypeSerializer,
    PreferenceNotificationSerializer, NotificationLueSerializer
)
from comptes.permissions import EstAdminSysteme, EstProprietaireHopital

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'priorite']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtrer par utilisateur (chacun ne voit que ses notifications)
        queryset = queryset.filter(utilisateur=user)
        
        # Filtrer par tenant
        if user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        
        # Filtrer par lecture
        est_lu = self.request.query_params.get('est_lu')
        if est_lu == 'true':
            queryset = queryset.filter(est_lu=True)
        elif est_lu == 'false':
            queryset = queryset.filter(est_lu=False)
        
        # Filtrer par priorité
        priorite = self.request.query_params.get('priorite')
        if priorite:
            queryset = queryset.filter(priorite=priorite)
        
        # Filtrer par type
        type_id = self.request.query_params.get('type_id')
        if type_id:
            queryset = queryset.filter(type_id=type_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Surcharge pour ajouter automatiquement le tenant"""
        serializer.save(tenant=self.request.user.hopital)
    
    @action(detail=False, methods=['get'])
    def non_lues(self, request):
        """Récupérer les notifications non lues"""
        queryset = self.get_queryset().filter(est_lu=False)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'notifications': serializer.data,
            'total': queryset.count()
        })
    
    @action(detail=False, methods=['post'])
    def marquer_toutes_lues(self, request):
        """Marquer toutes les notifications comme lues"""
        notifications = self.get_queryset().filter(est_lu=False)
        
        count = notifications.count()
        notifications.update(est_lu=True, date_lu=timezone.now())
        
        return Response({
            'message': f'{count} notification(s) marquée(s) comme lue(s)',
            'count': count
        })
    
    @action(detail=True, methods=['post'])
    def marquer_comme_lue(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        
        # Vérifier que la notification appartient à l'utilisateur
        if notification.utilisateur != request.user:
            return Response(
                {'error': 'Cette notification ne vous appartient pas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.marquer_comme_lu()
        
        return Response({
            'message': 'Notification marquée comme lue',
            'notification': self.get_serializer(notification).data
        })
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques des notifications"""
        user = request.user
        
        total_notifications = self.get_queryset().count()
        notifications_lues = self.get_queryset().filter(est_lu=True).count()
        notifications_non_lues = self.get_queryset().filter(est_lu=False).count()
        
        # Notifications par priorité
        par_priorite = self.get_queryset().values('priorite').annotate(
            total=models.Count('notification_id')
        )
        
        # Notifications par type
        par_type = self.get_queryset().values('type__nom').annotate(
            total=models.Count('notification_id')
        )
        
        data = {
            'total': total_notifications,
            'lues': notifications_lues,
            'non_lues': notifications_non_lues,
            'par_priorite': list(par_priorite),
            'par_type': list(par_type),
        }
        
        return Response(data)

class PreferenceNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les préférences de notifications"""
    queryset = PreferenceNotification.objects.all()
    serializer_class = PreferenceNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Chacun ne voit que ses préférences
        return queryset.filter(utilisateur=user)
    
    @action(detail=False, methods=['get'])
    def mes_preferences(self, request):
        """Récupérer les préférences de l'utilisateur connecté"""
        try:
            preferences = PreferenceNotification.objects.get(utilisateur=request.user)
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        except PreferenceNotification.DoesNotExist:
            # Créer des préférences par défaut
            preferences = PreferenceNotification.objects.create(utilisateur=request.user)
            serializer = self.get_serializer(preferences)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class NotificationTypeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les types de notifications"""
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tenant']
    search_fields = ['nom', 'description']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtrer par tenant
        if user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        
        return queryset
    
    def perform_create(self, serializer):
        """Surcharge pour ajouter automatiquement le tenant"""
        serializer.save(tenant=self.request.user.hopital)