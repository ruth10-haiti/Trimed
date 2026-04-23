from rest_framework import permissions

class PeutGererSalles(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin-systeme', 'proprietaire-hopital', 'medecin', 'secretaire']