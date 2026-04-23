from django.contrib import admin
from .models import (
    Patient, AdressePatient, PersonneAContacter,
    AssurancePatient, AllergiePatient, AntecedentMedical,
    SuiviPatient
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'hopital', 'numero_dossier_medical', 'cree_le')
    list_filter = ('hopital', 'sexe')
    search_fields = ('nom', 'prenom', 'numero_dossier_medical', 'telephone')
    readonly_fields = ('cree_le', 'modifie_le')
    
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'sexe')
        }),
        ('Identification', {
            'fields': ('numero_dossier_medical', 'numero_identification_nationale')
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'email')
        }),
        ('Relations', {
            'fields': ('hopital', 'utilisateur')
        }),
        ('Système', {
            'fields': ('cree_le', 'modifie_le')
        }),
    )

@admin.register(AdressePatient)
class AdressePatientAdmin(admin.ModelAdmin):
    list_display = ('patient', 'ville', 'pays', 'cree_le')
    list_filter = ('pays', 'ville')
    search_fields = ('patient__nom', 'patient__prenom', 'ville', 'code_postal')

@admin.register(AllergiePatient)
class AllergiePatientAdmin(admin.ModelAdmin):
    list_display = ('patient', 'nom_allergie', 'cree_le')
    search_fields = ('patient__nom', 'patient__prenom', 'nom_allergie')

@admin.register(SuiviPatient)
class SuiviPatientAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date_suivi', 'poids', 'taille', 'temperature')
    list_filter = ('date_suivi',)
    search_fields = ('patient__nom', 'patient__prenom')