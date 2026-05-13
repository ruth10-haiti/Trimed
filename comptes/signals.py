from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Utilisateur, EmailVerificationToken
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Utilisateur)
def creer_profils_associes(sender, instance, created, **kwargs):
    """
    Crée automatiquement des profils spécifiques selon le rôle
    """
    if created:
        if instance.role == 'medecin':
            # Créer un profil médecin
            from medical.models import Medecin
            nom_parts = instance.nom_complet.split(' ', 1)
            nom = nom_parts[0] if len(nom_parts) > 0 else instance.nom_complet
            prenom = nom_parts[1] if len(nom_parts) > 1 else ''
            
            Medecin.objects.create(
                utilisateur=instance,
                hopital=instance.hopital,
                nom=nom,
                prenom=prenom,
                email_professionnel=instance.email,
                cree_par_utilisateur=instance,
                cree_le=timezone.now()
            )
        
        elif instance.role == 'patient':
            # Créer un profil patient
            from patients.models import Patient
            nom_parts = instance.nom_complet.split(' ', 1)
            nom = nom_parts[0] if len(nom_parts) > 0 else instance.nom_complet
            prenom = nom_parts[1] if len(nom_parts) > 1 else ''
            
            # Générer un numéro de dossier unique
            from datetime import datetime
            numero_dossier = f"PAT{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            Patient.objects.create(
                utilisateur=instance,
                hopital=instance.hopital,
                nom=nom,
                prenom=prenom,
                email=instance.email,
                numero_dossier_medical=numero_dossier,
                cree_le=timezone.now()
            )


@receiver(post_save, sender=Utilisateur)
def logger_modification_utilisateur(sender, instance, **kwargs):
    """
    Logger les modifications d'utilisateurs
    """
    # Log seulement pour les modifications importantes
    if not kwargs.get('created'):
        logger.info(f"Utilisateur modifié: {instance.email} (ID: {instance.pk})")