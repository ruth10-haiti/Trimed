# authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.utils.translation import gettext_lazy as _

class TenantJWTAuthentication(JWTAuthentication):
    """
    Authentification JWT personnalisée avec vérification du tenant
    """
    
    def get_user(self, validated_token):
        """
        Récupérer l'utilisateur avec vérification du tenant actif
        """
        try:
            user_id = validated_token[self.user_id_field]
            user = self.user_model.objects.get(**{self.user_id_field: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_('Utilisateur non trouvé'), code='user_not_found')
        
        # Vérifier si l'utilisateur est actif
        if not user.is_active:
            raise AuthenticationFailed(_('Utilisateur désactivé'), code='user_inactive')
        
        # Vérifier si le tenant de l'utilisateur est actif
        if user.hopital and user.hopital.statut != 'actif':
            raise AuthenticationFailed(
                _('L\'hôpital est inactif ou suspendu'),
                code='hospital_inactive'
            )
        
        return user