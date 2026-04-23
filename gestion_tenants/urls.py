from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, ParametreHopitalViewSet

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'parametres', ParametreHopitalViewSet, basename='parametre')

urlpatterns = [
    path('', include(router.urls)),
]