# rendez_vous/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RendezVousViewSet, RendezVousTypeViewSet, RendezVousStatutViewSet
)

router = DefaultRouter()
router.register(r'types', RendezVousTypeViewSet, basename='rendez-vous-types')
router.register(r'statuts', RendezVousStatutViewSet, basename='rendez-vous-statuts')
router.register(r'', RendezVousViewSet, basename='rendez-vous')

urlpatterns = [
    path('', include(router.urls)),
]