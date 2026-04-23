from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedecinViewSet, SpecialiteViewSet, GroupeSanguinViewSet,
    ConsultationViewSet, OrdonnanceViewSet, ExamenMedicalViewSet,
    PrescriptionViewSet
)

router = DefaultRouter()
router.register(r'medecins', MedecinViewSet, basename='medecin')
router.register(r'specialites', SpecialiteViewSet, basename='specialite')
router.register(r'groupes-sanguins', GroupeSanguinViewSet, basename='groupe-sanguin')
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'ordonnances', OrdonnanceViewSet, basename='ordonnance')
router.register(r'examens', ExamenMedicalViewSet, basename='examen-medical')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
]
