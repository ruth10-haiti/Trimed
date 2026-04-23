from django.contrib import admin
from .models import TypeSalle, SalleMedicale, ReservationSalle

@admin.register(TypeSalle)
class TypeSalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'tenant')
    list_filter = ('tenant',)

@admin.register(SalleMedicale)
class SalleMedicaleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'type_salle', 'capacite', 'statut')
    list_filter = ('tenant', 'type_salle', 'statut')
    search_fields = ('nom', 'code')

@admin.register(ReservationSalle)
class ReservationSalleAdmin(admin.ModelAdmin):
    list_display = ('salle', 'date_debut', 'date_fin', 'utilisateur', 'statut')
    list_filter = ('statut', 'salle__tenant')
    search_fields = ('salle__nom',)