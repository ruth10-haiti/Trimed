from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    list_display = ('email', 'nom_complet', 'role', 'hopital', 'is_active', 'cree_le')
    list_filter = ('role', 'is_active', 'hopital', 'is_staff')
    search_fields = ('email', 'nom_complet')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom_complet',)}),
        ('Rôle et accès', {'fields': ('role', 'hopital', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'cree_le', 'derniere_connexion')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom_complet', 'password1', 'password2', 'role', 'hopital'),
        }),
    )
    
    readonly_fields = ('cree_le', 'last_login', 'derniere_connexion')