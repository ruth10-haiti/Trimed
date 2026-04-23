from rest_framework import serializers
from django.utils import timezone
from .models import NotificationType, Notification, PreferenceNotification
from comptes.serializers import UtilisateurSerializer
from gestion_tenants.serializers import TenantSerializer

class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = '__all__'
        read_only_fields = ('type_id', 'created_at', 'updated_at')
    
    def validate_nom(self, value):
        """Vérifier l'unicité du nom dans le tenant"""
        tenant = self.context['request'].user.hopital
        if NotificationType.objects.filter(tenant=tenant, nom=value).exists():
            raise serializers.ValidationError("Ce type de notification existe déjà")
        return value

class NotificationSerializer(serializers.ModelSerializer):
    type_detail = NotificationTypeSerializer(source='type', read_only=True)
    utilisateur_detail = UtilisateurSerializer(source='utilisateur', read_only=True)
    tenant_detail = TenantSerializer(source='tenant', read_only=True)
    cible_url = serializers.SerializerMethodField()
    priorite_color = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'notification_id', 'tenant', 'tenant_detail', 'type', 'type_detail',
            'utilisateur', 'utilisateur_detail', 'titre', 'message',
            'priorite', 'priorite_color', 'donnees', 'cible_type', 'cible_id',
            'cible_url', 'est_lu', 'est_envoyee', 'created_at', 'date_lu',
            'date_envoyee'
        ]
        read_only_fields = (
            'notification_id', 'created_at', 'date_lu', 'date_envoyee'
        )
    
    def get_cible_url(self, obj):
        return obj.get_cible_url()
    
    def get_priorite_color(self, obj):
        return obj.get_priorite_color()
    
    def validate(self, data):
        """Validation de la notification"""
        # S'assurer que l'utilisateur fait partie du tenant
        utilisateur = data.get('utilisateur')
        tenant = data.get('tenant', self.context['request'].user.hopital)
        
        if utilisateur and tenant and utilisateur.hopital != tenant:
            raise serializers.ValidationError({
                'utilisateur': 'Cet utilisateur n\'appartient pas à ce tenant'
            })
        
        return data

class NotificationLueSerializer(serializers.Serializer):
    """Serializer pour marquer une notification comme lue"""
    
    notification_id = serializers.IntegerField(required=True)
    
    def validate_notification_id(self, value):
        try:
            notification = Notification.objects.get(pk=value)
        except Notification.DoesNotExist:
            raise serializers.ValidationError("Notification non trouvée")
        
        # Vérifier que la notification appartient à l'utilisateur
        request = self.context['request']
        if notification.utilisateur != request.user:
            raise serializers.ValidationError("Cette notification ne vous appartient pas")
        
        return value

class PreferenceNotificationSerializer(serializers.ModelSerializer):
    utilisateur_detail = UtilisateurSerializer(source='utilisateur', read_only=True)
    
    class Meta:
        model = PreferenceNotification
        fields = '__all__'
        read_only_fields = ('preference_id', 'created_at', 'updated_at', 'utilisateur')