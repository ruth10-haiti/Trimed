from rest_framework import permissions

class PeutModifierTenant(permissions.BasePermission):
    """
    Permission pour modifier un tenant
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role == 'admin-systeme'
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
    
class PeutVoirTenant(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True

        if not request.user.is_authenticated:
            return False

        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True

        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            return hasattr(obj, 'proprietaire_utilisateur') and obj.proprietaire_utilisateur == request.user

        return hasattr(request.user, 'hopital') and request.user.hopital == obj