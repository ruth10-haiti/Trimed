# admin.py
from django.contrib import admin
from .models import (
    GroupeSanguin, Specialite, Medecin,
    Consultation, Ordonnance, ExamenMedical,
    Prescription, LignePrescription
)

@admin.register(GroupeSanguin)
class GroupeSanguinAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('code',)

@admin.register(Specialite)
class SpecialiteAdmin(admin.ModelAdmin):
    list_display = ('nom_specialite',)
    search_fields = ('nom_specialite', 'description')

@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'hopital', 'specialite_principale', 'cree_le')
    list_filter = ('hopital', 'specialite_principale', 'sexe')
    search_fields = ('nom', 'prenom', 'email_professionnel', 'numero_identification')
    readonly_fields = ('cree_le', 'modifie_le')
    
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('nom', 'prenom', 'sexe', 'date_naissance')
        }),
        ('Coordonnées Professionnelles', {
            'fields': ('telephone', 'email_professionnel')
        }),
        ('Identification', {
            'fields': ('numero_identification', 'numero_matricule_professionnel')
        }),
        ('Affectation', {
            'fields': ('hopital', 'specialite_principale')
        }),
        ('Relations', {
            'fields': ('utilisateur', 'cree_par_utilisateur', 'modifie_par_utilisateur')
        }),
        ('Système', {
            'fields': ('cree_le', 'modifie_le')
        }),
    )

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_consultation', 'motif', 'created_at')
    list_filter = ('tenant', 'medecin', 'date_consultation')
    search_fields = ('patient__nom', 'patient__prenom', 'medecin__nom', 'motif')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'patient', 'medecin', 'rendez_vous')
        }),
        ('Consultation', {
            'fields': ('date_consultation', 'motif', 'diagnostic_principal', 'notes')
        }),
        ('Système', {
            'fields': ('created_at', 'updated_at')
        }),
    )