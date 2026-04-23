from django.contrib import admin
from .models import Chambre, Lit, Admission

@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tenant', 'type_chambre', 'capacite', 'statut', 'etage')
    list_filter = ('tenant', 'type_chambre', 'statut')
    search_fields = ('numero',)

@admin.register(Lit)
class LitAdmin(admin.ModelAdmin):
    list_display = ('numero_lit', 'chambre', 'statut')
    list_filter = ('chambre__tenant', 'statut')
    search_fields = ('numero_lit',)

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'lit', 'date_admission', 'date_sortie', 'statut')
    list_filter = ('statut', 'lit__chambre__tenant')
    search_fields = ('patient__nom', 'patient__prenom')