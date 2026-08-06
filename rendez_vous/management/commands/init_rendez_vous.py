# rendez_vous/management/commands/init_rendez_vous.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rendez_vous.models import RendezVousType, RendezVousStatut
from gestion_tenants.models import Tenant

class Command(BaseCommand):
    help = 'Initialise les types et statuts de rendez-vous par défaut'

    def handle(self, *args, **options):
        tenant = Tenant.objects.first()
        
        if not tenant:
            self.stdout.write(self.style.WARNING('Aucun tenant trouvé. Création d\'un tenant par défaut...'))
            tenant = Tenant.objects.create(
                nom='Hôpital par défaut',
                code='DEFAULT'
            )
            self.stdout.write(self.style.SUCCESS(f'Tenant créé: {tenant.nom}'))

        types_defaut = [
            {'nom': 'Consultation', 'duree_defaut': 30, 'couleur': '#3498db', 'description': 'Consultation médicale générale'},
            {'nom': 'Urgence', 'duree_defaut': 15, 'couleur': '#e74c3c', 'description': 'Cas urgent nécessitant une attention immédiate'},
            {'nom': 'Contrôle', 'duree_defaut': 20, 'couleur': '#2ecc71', 'description': 'Visite de contrôle ou suivi'},
            {'nom': 'Spécialiste', 'duree_defaut': 45, 'couleur': '#9b59b6', 'description': 'Consultation avec un médecin spécialiste'},
            {'nom': 'Téléconsultation', 'duree_defaut': 25, 'couleur': '#1abc9c', 'description': 'Consultation à distance'},
        ]

        for type_data in types_defaut:
            obj, created = RendezVousType.objects.get_or_create(
                tenant=tenant,
                nom=type_data['nom'],
                defaults=type_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Type créé: {obj.nom}'))

        statuts_defaut = [
            {'nom': 'Planifié', 'couleur': '#3498db', 'est_confirme': False, 'est_annule': False, 'est_termine': False, 'description': 'Rendez-vous planifié'},
            {'nom': 'Confirmé', 'couleur': '#2ecc71', 'est_confirme': True, 'est_annule': False, 'est_termine': False, 'description': 'Rendez-vous confirmé par le patient'},
            {'nom': 'En attente', 'couleur': '#f39c12', 'est_confirme': False, 'est_annule': False, 'est_termine': False, 'description': 'En attente de confirmation'},
            {'nom': 'Annulé', 'couleur': '#e74c3c', 'est_confirme': False, 'est_annule': True, 'est_termine': False, 'description': 'Rendez-vous annulé'},
            {'nom': 'Terminé', 'couleur': '#95a5a6', 'est_confirme': True, 'est_annule': False, 'est_termine': True, 'description': 'Rendez-vous terminé'},
            {'nom': 'Reporté', 'couleur': '#9b59b6', 'est_confirme': False, 'est_annule': False, 'est_termine': False, 'description': 'Rendez-vous reporté à une autre date'},
        ]

        for statut_data in statuts_defaut:
            obj, created = RendezVousStatut.objects.get_or_create(
                tenant=tenant,
                nom=statut_data['nom'],
                defaults=statut_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Statut créé: {obj.nom}'))

        self.stdout.write(self.style.SUCCESS('✅ Initialisation terminée avec succès!'))