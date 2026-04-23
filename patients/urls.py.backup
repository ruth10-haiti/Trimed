from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, AdressePatientViewSet,
    SuiviPatientViewSet, AllergiePatientViewSet,
    AntecedentMedicalViewSet
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'adresses', AdressePatientViewSet, basename='adresse')
router.register(r'suivis', SuiviPatientViewSet, basename='suivi')
router.register(r'allergies', AllergiePatientViewSet, basename='allergie')
router.register(r'antecedents', AntecedentMedicalViewSet, basename='antecedent')

urlpatterns = [
    path('', include(router.urls)),
]