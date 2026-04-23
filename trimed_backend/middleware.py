# backend/trimedh_api/middleware.py
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    """
    Middleware pour gérer le tenant actif
    """
    
    def process_request(self, request):
        """
        Déterminer le tenant basé sur l'utilisateur authentifié
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Définir le tenant dans la requête pour un accès facile
            request.tenant = request.user.hopital
            
            # Log de l'accès tenant
            logger.info(f"User {request.user.email} accessing tenant {request.tenant}")

class LoggingMiddleware(MiddlewareMixin):
    """
    Middleware pour logger les requêtes et réponses
    """
    
    def process_request(self, request):
        """
        Logger les requêtes entrantes
        """
        if request.path.startswith('/api/'):
            logger.info(
                f"API Request: {request.method} {request.path} "
                f"User: {request.user if hasattr(request, 'user') else 'Anonymous'}"
            )
    
    def process_response(self, request, response):
        """
        Logger les réponses sortantes
        """
        if request.path.startswith('/api/'):
            log_data = {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            }
            logger.info(f"API Response: {json.dumps(log_data)}")
        
        return response

class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    Middleware pour gérer les exceptions de manière centralisée
    """
    
    def process_exception(self, request, exception):
        """
        Gérer les exceptions et retourner des réponses JSON appropriées
        """
        # Log de l'erreur
        logger.error(f"Exception occurred: {str(exception)}", exc_info=True)
        
        # Gérer les erreurs JWT
        if isinstance(exception, (InvalidToken, TokenError)):
            return JsonResponse(
                {'error': 'Token invalide ou expiré', 'detail': str(exception)},
                status=401
            )
        
        # Gérer les autres exceptions
        return JsonResponse(
            {'error': 'Erreur interne du serveur', 'detail': str(exception)},
            status=500
        )