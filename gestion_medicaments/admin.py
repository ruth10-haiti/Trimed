from django.contrib import admin
from .models import MedicamentCategorie, Medicament

@admin.register(MedicamentCategorie)
class MedicamentCategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('nom', 'description')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'nom', 'description')
        }),
        ('Système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'forme_pharmaceutique', 'categorie', 'tenant', 'created_at')
    list_filter = ('tenant', 'categorie', 'forme_pharmaceutique')
    search_fields = ('nom', 'description', 'dosage_standard')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'nom', 'forme_pharmaceutique', 'dosage_standard')
        }),
        ('Classification', {
            'fields': ('categorie',)
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')