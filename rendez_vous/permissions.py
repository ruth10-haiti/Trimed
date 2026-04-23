from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta

class PeutCreerRendezVous(permissions.BasePermission):
    """
    Permission pour créer un rendez-vous
    """
    
    def has_permission(self, request, view):
        # Tout utilisateur authentifié peut créer un rendez-vous
        return request.user.is_authenticated


class PeutModifierRendezVous(permissions.BasePermission):
    """
    Permission pour modifier un rendez-vous
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système peut tout modifier
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire peut modifier les rendez-vous de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            return hasattr(request.user, 'hopital') and hasattr(obj, 'tenant') and obj.tenant == request.user.hopital
        
        # Patients ne peuvent modifier que leurs propres rendez-vous
        if hasattr(request.user, 'role') and request.user.role == 'patient':
            return hasattr(request.user, 'patient_lie') and hasattr(obj, 'patient') and request.user.patient_lie == obj.patient
        
        # Médecins ne peuvent modifier que leurs propres rendez-vous
        if hasattr(request.user, 'role') and request.user.role == 'medecin':
            return hasattr(request.user, 'medecin_lie') and hasattr(obj, 'medecin') and request.user.medecin_lie == obj.medecin
        
        # Personnel peut modifier tous les rendez-vous de leur tenant
        if hasattr(request.user, 'role') and request.user.role in ['personnel', 'secretaire', 'infirmier']:
            return hasattr(request.user, 'hopital') and hasattr(obj, 'tenant') and request.user.hopital == obj.tenant
        
        return False


class PeutAnnulerRendezVous(permissions.BasePermission):
    """
    Permission pour annuler un rendez-vous
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système peut tout annuler
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire peut annuler les rendez-vous de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            return hasattr(request.user, 'hopital') and hasattr(obj, 'tenant') and obj.tenant == request.user.hopital
        
        # Les patients peuvent annuler leurs rendez-vous jusqu'à 24h avant
        if hasattr(request.user, 'role') and request.user.role == 'patient':
            if hasattr(request.user, 'patient_lie') and hasattr(obj, 'patient') and request.user.patient_lie == obj.patient:
                # Vérifier que le rendez-vous est dans plus de 24h
                if hasattr(obj, 'date_heure') and obj.date_heure:
                    return obj.date_heure > timezone.now() + timedelta(hours=24)
            return False
        
        # Les médecins et personnel peuvent annuler à tout moment
        if hasattr(request.user, 'role') and request.user.role in ['medecin', 'personnel', 'secretaire', 'infirmier']:
            return hasattr(request.user, 'hopital') and hasattr(obj, 'tenant') and obj.tenant == request.user.hopital
        
        return False