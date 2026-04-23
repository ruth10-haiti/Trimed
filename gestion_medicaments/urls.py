from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicamentViewSet, MedicamentCategorieViewSet

router = DefaultRouter()
router.register(r'categories', MedicamentCategorieViewSet, basename='medicament-categorie')
router.register(r'', MedicamentViewSet, basename='medicament')

urlpatterns = [
    path('', include(router.urls)),
]