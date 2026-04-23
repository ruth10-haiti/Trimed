# comptes/permissions.py
from rest_framework import permissions
from .models import Utilisateur

class EstAdminSysteme(permissions.BasePermission):
    """Permission pour les administrateurs système"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role == 'admin-systeme'
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EstProprietaireHopital(permissions.BasePermission):
    """Permission pour les propriétaires d'hôpital"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital'
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EstMedecin(permissions.BasePermission):
    """Permission pour les médecins"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role == 'medecin'
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EstPersonnel(permissions.BasePermission):
    """Permission pour le personnel (infirmier, secrétaire, etc.)"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        roles_personnel = ['personnel', 'secretaire', 'infirmier']
        return hasattr(request.user, 'role') and request.user.role in roles_personnel
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EstPatient(permissions.BasePermission):
    """Permission pour les patients"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role == 'patient'
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class PeutModifierUtilisateur(permissions.BasePermission):
    """
    Permission pour modifier un utilisateur
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # L'utilisateur peut modifier son propre profil
        if obj == request.user:
            return True
        
        # Les admins système peuvent modifier tous les utilisateurs
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Les propriétaires peuvent modifier les utilisateurs de leur tenant
        if (hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital' and 
            hasattr(request.user, 'hopital') and request.user.hopital and 
            hasattr(obj, 'hopital') and obj.hopital == request.user.hopital):
            return True
        
        return False


class EstDansMemesTenant(permissions.BasePermission):
    """
    Permission pour s'assurer que l'utilisateur accède uniquement 
    aux ressources de son propre tenant
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système peut tout voir
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        user_hopital = getattr(request.user, 'hopital', None)
        if not user_hopital:
            return False
        
        # Vérifier si l'objet a un attribut tenant ou hopital
        if hasattr(obj, 'tenant'):
            return obj.tenant == user_hopital
        elif hasattr(obj, 'hopital'):
            return obj.hopital == user_hopital
        elif isinstance(obj, Utilisateur):
            return obj.hopital == user_hopital
        
        return False


class PeutGererFacturation(permissions.BasePermission):
    """
    Permission pour gérer la facturation
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role in ['admin-systeme', 'proprietaire-hopital']
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire peut voir les factures de son tenant
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            return hasattr(obj, 'tenant') and obj.tenant == request.user.hopital
        
        return False


class PeutVoirFactures(permissions.BasePermission):
    """
    Permission pour voir les factures
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        return hasattr(obj, 'tenant') and obj.tenant == request.user.hopital


# ========== PERMISSIONS POUR LES MÉDICAMENTS ==========

class PeutGererMedicaments(permissions.BasePermission):
    """
    Permission pour gérer les médicaments (CRUD complet)
    Seuls les admin système et propriétaires d'hôpital peuvent gérer
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Admin système ou propriétaire d'hôpital
        roles_autorises = ['admin-systeme', 'proprietaire-hopital']
        return hasattr(request.user, 'role') and request.user.role in roles_autorises
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système peut tout faire
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire peut gérer les médicaments de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            if hasattr(obj, 'tenant') and hasattr(request.user, 'hopital'):
                return obj.tenant == request.user.hopital
            elif hasattr(obj, 'hopital') and hasattr(request.user, 'hopital'):
                return obj.hopital == request.user.hopital
        
        return False


class PeutModifierStock(permissions.BasePermission):
    """
    Permission pour modifier le stock
    Admin système, propriétaires d'hôpital et médecins peuvent modifier
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Admin système, propriétaire ou médecin
        roles_autorises = ['admin-systeme', 'proprietaire-hopital', 'medecin']
        return hasattr(request.user, 'role') and request.user.role in roles_autorises
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système peut tout faire
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Propriétaire peut modifier le stock de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'proprietaire-hopital':
            if hasattr(obj, 'tenant') and hasattr(request.user, 'hopital'):
                return obj.tenant == request.user.hopital
            elif hasattr(obj, 'hopital') and hasattr(request.user, 'hopital'):
                return obj.hopital == request.user.hopital
        
        # Médecin peut modifier le stock de son hôpital
        if hasattr(request.user, 'role') and request.user.role == 'medecin':
            if hasattr(obj, 'tenant') and hasattr(request.user, 'hopital'):
                return obj.tenant == request.user.hopital
            elif hasattr(obj, 'hopital') and hasattr(request.user, 'hopital'):
                return obj.hopital == request.user.hopital
        
        return False


class PeutVoirMedicaments(permissions.BasePermission):
    """
    Permission pour voir les médicaments
    Tous les utilisateurs authentifiés peuvent voir
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin système voit tout
        if hasattr(request.user, 'role') and request.user.role == 'admin-systeme':
            return True
        
        # Les autres voient seulement les médicaments de leur hôpital
        if hasattr(request.user, 'hopital') and request.user.hopital:
            if hasattr(obj, 'tenant'):
                return obj.tenant == request.user.hopital
            elif hasattr(obj, 'hopital'):
                return obj.hopital == request.user.hopital
        
        return False