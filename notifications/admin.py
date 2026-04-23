from django.contrib import admin
from .models import NotificationType, Notification

@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('nom', 'description', 'template')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'nom', 'description')
        }),
        ('Configuration', {
            'fields': ('template', 'canal')
        }),
        ('Système', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'type', 'est_lu', 'created_at')
    list_filter = ('tenant', 'type', 'est_lu', 'priorite')
    search_fields = ('titre', 'message', 'utilisateur__email')
    readonly_fields = ('created_at', 'date_lu')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('tenant', 'type', 'utilisateur')
        }),
        ('Contenu', {
            'fields': ('titre', 'message', 'priorite')
        }),
        ('État', {
            'fields': ('est_lu', 'date_lu')
        }),
        ('Système', {
            'fields': ('created_at',)
        }),
    )