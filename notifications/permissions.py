from rest_framework import permissions

class PeutVoirNotifications(permissions.BasePermission):
    """
    Permission pour voir les notifications
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système voit tout
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Chacun ne peut voir que ses propres notifications
        return hasattr(obj, 'utilisateur') and obj.utilisateur == request.user


class PeutGererTypesNotification(permissions.BasePermission):
    """
    Permission pour gérer les types de notifications
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role in ['admin-systeme', 'proprietaire-hopital']
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)