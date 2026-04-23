from rest_framework import permissions

class PeutGererMedicaments(permissions.BasePermission):
    """
    Permission pour gérer les médicaments
    """
    
    def has_permission(self, request, view):
        # Seuls le personnel peut gérer les médicaments
        return request.user.role in ['personnel', 'secretaire', 'infirmier', 'medecin']

class PeutModifierStock(permissions.BasePermission):
    """
    Permission pour modifier le stock
    """
    
    def has_permission(self, request, view):
        # Seul le personnel spécifique peut modifier le stock
        return request.user.role in ['personnel', 'infirmier']