from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TypeSalleViewSet, SalleMedicaleViewSet, ReservationSalleViewSet

router = DefaultRouter()
router.register(r'type-salles', TypeSalleViewSet)
router.register(r'salles', SalleMedicaleViewSet)
router.register(r'reservations', ReservationSalleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
