from rest_framework import permissions

class PeutAccederPatient(permissions.BasePermission):
    """
    Permission pour accéder à un patient
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système voit tout
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire voit les patients de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            return hasattr(request.user, 'hopital') and hasattr(obj, 'hopital') and obj.hopital == request.user.hopital
        
        # Patients ne voient que leur propre dossier
        if hasattr(request.user, 'role') and request.user.role == 'patient':
            return hasattr(request.user, 'patient_lie') and request.user.patient_lie == obj
        
        # Médecins et personnel voient les patients de leur tenant
        if hasattr(request.user, 'role') and request.user.role in ['medecin', 'personnel', 'infirmier', 'secretaire']:
            return hasattr(request.user, 'hopital') and hasattr(obj, 'hopital') and obj.hopital == request.user.hopital
        
        return False


class PeutModifierPatient(permissions.BasePermission):
    """
    Permission pour modifier un patient
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role in ['medecin', 'personnel', 'infirmier', 'secretaire', 'proprietaire-hopital', 'admin-systeme']
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système peut tout modifier
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire peut modifier les patients de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            return hasattr(request.user, 'hopital') and hasattr(obj, 'hopital') and obj.hopital == request.user.hopital
        
        # Médecins et personnel peuvent modifier les patients de leur tenant
        if hasattr(request.user, 'role') and request.user.role in ['medecin', 'personnel', 'infirmier', 'secretaire']:
            return hasattr(request.user, 'hopital') and hasattr(obj, 'hopital') and obj.hopital == request.user.hopital
        
        return False