from django.contrib import admin
from .models import Tenant, ParametreHopital

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email_professionnel', 'type_abonnement', 'statut', 'cree_le')
    list_filter = ('statut', 'type_abonnement', 'statut_verification_document')
    search_fields = ('nom', 'email_professionnel', 'directeur')
    readonly_fields = ('cree_le', 'date_verification')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('nom', 'adresse', 'telephone', 'email_professionnel')
        }),
        ('Direction', {
            'fields': ('directeur', 'nombre_de_lits')
        }),
        ('Identification', {
            'fields': ('numero_enregistrement', 'documents_justificatifs')
        }),
        ('État', {
            'fields': ('statut', 'type_abonnement', 'statut_verification_document')
        }),
        ('Validation', {
            'fields': ('verifie_par', 'date_verification')
        }),
        ('Système', {
            'fields': ('nom_schema_base_de_donnees', 'cree_par_utilisateur', 'proprietaire_utilisateur')
        }),
    )

@admin.register(ParametreHopital)
class ParametreHopitalAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'fuseau_horaire', 'langue', 'devise')
    list_filter = ('langue', 'devise')