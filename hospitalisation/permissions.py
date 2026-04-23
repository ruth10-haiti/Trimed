from rest_framework import permissions

class EstAdminHopital(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin-systeme', 'proprietaire-hopital']

class PeutGererHospitalisation(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin-systeme', 'proprietaire-hopital', 'medecin', 'infirmier']