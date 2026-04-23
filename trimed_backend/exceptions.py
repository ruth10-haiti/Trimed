from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Handler personnalisé pour les exceptions
    """
    # Appeler le handler par défaut d'abord
    response = exception_handler(exc, context)
    
    if response is not None:
        # Personnaliser la réponse d'erreur
        if isinstance(exc, DRFValidationError):
            # Formater les erreurs de validation
            errors = {}
            for field, messages in exc.detail.items():
                if isinstance(messages, list):
                    errors[field] = messages[0] if len(messages) == 1 else messages
                else:
                    errors[field] = messages
            
            response.data = {
                'error': 'Erreur de validation',
                'errors': errors,
                'status_code': response.status_code
            }
        
        elif response.status_code == 401:
            response.data = {
                'error': 'Non authentifié',
                'detail': str(exc.detail) if hasattr(exc, 'detail') else 'Token manquant ou invalide',
                'status_code': response.status_code
            }
        
        elif response.status_code == 403:
            response.data = {
                'error': 'Permission refusée',
                'detail': str(exc.detail) if hasattr(exc, 'detail') else 'Vous n\'avez pas la permission d\'effectuer cette action',
                'status_code': response.status_code
            }
        
        elif response.status_code == 404:
            response.data = {
                'error': 'Ressource non trouvée',
                'detail': str(exc.detail) if hasattr(exc, 'detail') else 'La ressource demandée n\'existe pas',
                'status_code': response.status_code
            }
    
    else:
        # Gérer les autres exceptions non gérées par DRF
        if isinstance(exc, DjangoValidationError):
            response = Response(
                {
                    'error': 'Erreur de validation',
                    'detail': str(exc),
                    'status_code': status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Log de l'erreur non gérée
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            
            response = Response(
                {
                    'error': 'Erreur interne du serveur',
                    'detail': 'Une erreur est survenue. Contactez l\'administrateur.',
                    'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return response