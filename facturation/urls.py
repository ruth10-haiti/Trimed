from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# TODO: Ajouter les routes nécessaires

urlpatterns = [
    path('', include(router.urls)),
]
