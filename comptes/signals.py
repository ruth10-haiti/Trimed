from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Utilisateur, EmailVerificationToken
import requests
import logging
from django.utils import timezone

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
    import logging
    logger = logging.getLogger(__name__)
    
    # Log seulement pour les modifications importantes
    if not kwargs.get('created'):
        logger.info(f"Utilisateur modifié: {instance.email} (ID: {instance.pk})")

logger = logging.getLogger(__name__)

def send_brevo_email(to_email, subject, html_content):
    """Envoi d'email via l'API Brevo (Sendinblue)"""
    api_key = settings.BREVO_API_KEY
    if not api_key:
        logger.error("BREVO_API_KEY non définie dans les settings")
        return False
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    data = {
        "sender": {"email": settings.DEFAULT_FROM_EMAIL, "name": "Trimed"},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Erreur envoi Brevo: {e}")
        return False

@receiver(post_save, sender=Utilisateur)
def send_verification_email(sender, instance, created, **kwargs):
    """Envoie un email de vérification à la création d'un utilisateur"""
    if created:
        token_obj = EmailVerificationToken.objects.create(utilisateur=instance)
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{token_obj.token}/"
        subject = "Vérifiez votre adresse email"
        html_message = f"""
        <h2>Bienvenue sur Trimed</h2>
        <p>Bonjour {instance.nom_complet},</p>
        <p>Merci de cliquer sur le lien ci-dessous pour vérifier votre compte :</p>
        <p><a href="{verification_link}">{verification_link}</a></p>
        <p>Ce lien expire dans 24 heures.</p>
        <p>Cordialement,<br>L'équipe Trimed</p>
        """
        send_brevo_email(instance.email, subject, html_message)