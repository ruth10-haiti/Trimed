from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Chambre, Lit, Admission
from .serializers import ChambreSerializer, LitSerializer, AdmissionSerializer
from .permissions import EstAdminHopital, PeutGererHospitalisation

class ChambreViewSet(viewsets.ModelViewSet):
    queryset = Chambre.objects.all()
    serializer_class = ChambreSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tenant', 'type_chambre', 'statut']
    search_fields = ['numero']
    ordering_fields = ['numero', 'etage']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [EstAdminHopital]
        else:
            permission_classes = [PeutGererHospitalisation]
        return [permission() for permission in permission_classes]

class LitViewSet(viewsets.ModelViewSet):
    queryset = Lit.objects.all()
    serializer_class = LitSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['chambre', 'statut']
    search_fields = ['numero_lit']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [EstAdminHopital]
        else:
            permission_classes = [PeutGererHospitalisation]
        return [permission() for permission in permission_classes]

class AdmissionViewSet(viewsets.ModelViewSet):
    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'lit', 'statut']
    ordering_fields = ['date_admission', 'date_sortie']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [PeutGererHospitalisation]
        else:
            permission_classes = [PeutGererHospitalisation]
        return [permission() for permission in permission_classes]