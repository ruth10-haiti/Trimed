from rest_framework import permissions

class PeutGererMedicaments(permissions.BasePermission):
    """
    Permission pour gérer les médicaments
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role in ['personnel', 'secretaire', 'infirmier', 'medecin', 'proprietaire-hopital', 'admin-systeme']
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class PeutModifierStock(permissions.BasePermission):
    """
    Permission pour modifier le stock
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role in ['personnel', 'infirmier', 'proprietaire-hopital', 'admin-systeme']
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système peut tout modifier
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire peut modifier le stock de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            return hasattr(obj, 'hopital') and obj.hopital == request.user.hopital
        
        # Personnel peut modifier le stock de son hôpital
        return hasattr(request.user, 'hopital') and hasattr(obj, 'hopital') and obj.hopital == request.user.hopital