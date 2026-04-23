# admin.py
from django.contrib import admin
from .models import (
    Plan, AbonnementStatut, PaiementMethode, PaiementStatut,
    InvoiceStatut, Abonnement, Paiement, Invoice,
    AbonnementRenouvellement, EssaiGratuit, Coupon, CouponTenant,
    TarifConsultation
)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix_mensuel', 'prix_annuel', 'actif', 'created_at')
    list_filter = ('actif',)
    search_fields = ('nom', 'description')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('nom', 'description')
        }),
        ('Tarification', {
            'fields': ('prix_mensuel', 'prix_annuel')
        }),
        ('Configuration', {
            'fields': ('actif',)
        }),
    )

@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'plan', 'statut', 'date_debut', 'date_fin', 'created_at')
    list_filter = ('statut', 'plan', 'date_debut')
    search_fields = ('tenant__nom', 'plan__nom')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'plan', 'statut')
        }),
        ('Période', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'abonnement', 'montant', 'methode', 'statut', 'date_paiement')
    list_filter = ('methode', 'statut', 'date_paiement')
    search_fields = ('tenant__nom', 'reference', 'abonnement__plan__nom')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'abonnement', 'methode', 'statut')
        }),
        ('Détails Paiement', {
            'fields': ('montant', 'date_paiement', 'reference')
        }),
        ('Système', {
            'fields': ('created_at',)
        }),
    )
    readonly_fields = ('created_at',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'tenant', 'paiement', 'montant', 'statut', 'date_emission')
    list_filter = ('statut', 'date_emission')
    search_fields = ('numero_facture', 'tenant__nom')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('paiement', 'tenant', 'statut')
        }),
        ('Détails Facture', {
            'fields': ('numero_facture', 'date_emission', 'date_echeance', 'montant', 'url_pdf')
        }),
        ('Système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')