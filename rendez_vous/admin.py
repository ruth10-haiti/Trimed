# admin.py
from django.contrib import admin
from .models import RendezVousType, RendezVousStatut, RendezVous

@admin.register(RendezVousType)
class RendezVousTypeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('nom', 'description')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'nom', 'description')
        }),
        ('Configuration', {
            'fields': ('duree_defaut', 'couleur')
        }),
    )

@admin.register(RendezVousStatut)
class RendezVousStatutAdmin(admin.ModelAdmin):
    list_display = ('nom', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('nom', 'description')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'nom', 'description')
        }),
    )

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_heure', 'type', 'statut', 'created_at')
    list_filter = ('tenant', 'type', 'statut', 'date_heure')
    search_fields = ('patient__nom', 'patient__prenom', 'medecin__nom', 'motif')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'patient', 'medecin', 'date_heure')
        }),
        ('Détails', {
            'fields': ('type', 'statut', 'motif')
        }),
        ('Notes', {
            'fields': ('notes', 'raison_annulation')
        }),
        ('Système', {
            'fields': ('created_at', 'updated_at')
        }),
    )