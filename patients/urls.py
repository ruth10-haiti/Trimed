from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, AdressePatientViewSet, PersonneAContacterViewSet,
    AssurancePatientViewSet, AllergiePatientViewSet, AntecedentMedicalViewSet,
    SuiviPatientViewSet
)

router = DefaultRouter()
router.register(r'', PatientViewSet, basename='patient')
router.register(r'adresses', AdressePatientViewSet, basename='adresse-patient')
router.register(r'contacts', PersonneAContacterViewSet, basename='contact-patient')
router.register(r'assurances', AssurancePatientViewSet, basename='assurance-patient')
router.register(r'allergies', AllergiePatientViewSet, basename='allergie-patient')
router.register(r'antecedents', AntecedentMedicalViewSet, basename='antecedent-patient')
router.register(r'suivis', SuiviPatientViewSet, basename='suivi-patient')

urlpatterns = [
    path('', include(router.urls)),
]
