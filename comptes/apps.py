from django.apps import AppConfig


class ComptesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comptes'
    verbose_name = 'Gestion des Comptes'
    
    def ready(self):
        import comptes.signals
