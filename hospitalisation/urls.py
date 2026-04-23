from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChambreViewSet, LitViewSet, AdmissionViewSet

router = DefaultRouter()
router.register(r'chambres', ChambreViewSet)
router.register(r'lits', LitViewSet)
router.register(r'admissions', AdmissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]