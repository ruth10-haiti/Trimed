from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint de vérification de santé de l'API"""
    return Response({
        'status': 'OK',
        'message': 'Trimed Backend API is running',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """Informations sur l'API"""
    return Response({
        'name': 'Trimed Backend API',
        'version': '1.0.0',
        'description': 'API pour la gestion hospitalière',
        'endpoints': {
            'auth': '/api/comptes/',
            'patients': '/api/patients/',
            'medical': '/api/medical/',
            'medicaments': '/api/medicaments/',
            'rendez_vous': '/api/rendez-vous/',
            'facturation': '/api/facturation/',
            'notifications': '/api/notifications/',
            'tenants': '/api/tenants/',
        },
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/'
        }
    })