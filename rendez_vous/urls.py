from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RendezVousViewSet, RendezVousTypeViewSet, RendezVousStatutViewSet
)

router = DefaultRouter()
router.register(r'', RendezVousViewSet, basename='rendez-vous')
router.register(r'types', RendezVousTypeViewSet, basename='rendez-vous-type')
router.register(r'statuts', RendezVousStatutViewSet, basename='rendez-vous-statut')

urlpatterns = [
    path('', include(router.urls)),
]
