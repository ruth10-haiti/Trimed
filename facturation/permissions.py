from rest_framework import permissions

class PeutGererFacturation(permissions.BasePermission):
    """
    Permission pour gérer la facturation
    """
    
    def has_permission(self, request, view):
        # Seuls les admins système et propriétaires peuvent gérer la facturation
        return request.user.role in ['admin-systeme', 'proprietaire-hopital']

class PeutVoirFactures(permissions.BasePermission):
    """
    Permission pour voir les factures
    """
    
    def has_permission(self, request, view):
        # Tout utilisateur authentifié peut voir les factures de son tenant
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Vérifier que l'utilisateur a accès à cette facture
        if request.user.role == 'admin-systeme':
            return True
        
        return obj.tenant == request.user.hopital