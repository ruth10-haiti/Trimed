from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TypeSalle, SalleMedicale, ReservationSalle
from .serializers import TypeSalleSerializer, SalleMedicaleSerializer, ReservationSalleSerializer
from .permissions import PeutGererSalles

class TypeSalleViewSet(viewsets.ModelViewSet):
    queryset = TypeSalle.objects.all()
    serializer_class = TypeSalleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tenant']
    search_fields = ['nom']

    def get_permissions(self):
        permission_classes = [PeutGererSalles]
        return [permission() for permission in permission_classes]

class SalleMedicaleViewSet(viewsets.ModelViewSet):
    queryset = SalleMedicale.objects.all()
    serializer_class = SalleMedicaleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tenant', 'type_salle', 'statut']
    search_fields = ['nom', 'code']
    ordering_fields = ['nom', 'created_at']

    def get_permissions(self):
        permission_classes = [PeutGererSalles]
        return [permission() for permission in permission_classes]

class ReservationSalleViewSet(viewsets.ModelViewSet):
    queryset = ReservationSalle.objects.all()
    serializer_class = ReservationSalleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['salle', 'utilisateur', 'statut']
    ordering_fields = ['date_debut', 'date_fin']

    def get_permissions(self):
        permission_classes = [PeutGererSalles]
        return [permission() for permission in permission_classes]