# models.py
from django.db import models
from django.utils import timezone
from django.utils.html import format_html

class NotificationType(models.Model):
    """TABLE NotificationType"""
    
    class Canal(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        APPLICATION = 'application', 'Application'
        TOUS = 'tous', 'Tous'
    
    type_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    template = models.TextField()
    canal = models.CharField(
        max_length=20,
        choices=Canal.choices,
        default=Canal.APPLICATION
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'notification_type'
        verbose_name = 'Type de notification'
        verbose_name_plural = 'Types de notifications'
        unique_together = ['tenant', 'nom']

class Notification(models.Model):
    """TABLE Notification"""
    
    class Priorite(models.TextChoices):
        FAIBLE = 'faible', 'Faible'
        MOYENNE = 'moyenne', 'Moyenne'
        ELEVEE = 'elevee', 'Élevée'
        URGENT = 'urgent', 'Urgent'
    
    notification_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        db_column='type_id'
    )
    utilisateur = models.ForeignKey(
        'comptes.Utilisateur',
        on_delete=models.CASCADE,
        db_column='utilisateur_id'
    )
    
    titre = models.CharField(max_length=255)
    message = models.TextField()
    priorite = models.CharField(
        max_length=20,
        choices=Priorite.choices,
        default=Priorite.MOYENNE
    )
    
    # Données supplémentaires (stockées en JSON)
    donnees = models.JSONField(null=True, blank=True)
    
    # Cible (optionnel)
    cible_type = models.CharField(max_length=100, null=True, blank=True)
    cible_id = models.IntegerField(null=True, blank=True)
    
    # État
    est_lu = models.BooleanField(default=False)
    est_envoyee = models.BooleanField(default=False)
    
    # Dates
    created_at = models.DateTimeField(default=timezone.now)
    date_lu = models.DateTimeField(null=True, blank=True)
    date_envoyee = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.titre} - {self.utilisateur}"
    
    def marquer_comme_lu(self):
        """Marquer la notification comme lue"""
        if not self.est_lu:
            self.est_lu = True
            self.date_lu = timezone.now()
            self.save()
    
    def marquer_comme_envoyee(self):
        """Marquer la notification comme envoyée"""
        if not self.est_envoyee:
            self.est_envoyee = True
            self.date_envoyee = timezone.now()
            self.save()
    
    def get_cible_url(self):
        """Obtenir l'URL de la cible si disponible"""
        if self.cible_type and self.cible_id:
            # Mapping des types de cible vers les URLs
            urls = {
                'patient': f'/patients/{self.cible_id}/',
                'rendez_vous': f'/rendez-vous/{self.cible_id}/',
                'consultation': f'/consultations/{self.cible_id}/',
                'paiement': f'/paiements/{self.cible_id}/',
                'abonnement': f'/abonnements/{self.cible_id}/',
            }
            return urls.get(self.cible_type, '#')
        return '#'
    
    def get_priorite_color(self):
        """Obtenir la couleur CSS selon la priorité"""
        colors = {
            'faible': 'info',
            'moyenne': 'warning',
            'elevee': 'danger',
            'urgent': 'dark',
        }
        return colors.get(self.priorite, 'secondary')
    
    def priorite_badge(self):
        """Retourne un badge HTML pour la priorité"""
        color = self.get_priorite_color()
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            self.get_priorite_display()
        )
    
    priorite_badge.short_description = 'Priorité'
    
    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'utilisateur', 'est_lu']),
            models.Index(fields=['created_at']),
        ]

class PreferenceNotification(models.Model):
    """Préférences de notifications par utilisateur"""
    
    preference_id = models.AutoField(primary_key=True)
    utilisateur = models.OneToOneField(
        'comptes.Utilisateur',
        on_delete=models.CASCADE,
        db_column='utilisateur_id'
    )
    
    # Notifications système
    notifications_email = models.BooleanField(default=True)
    notifications_sms = models.BooleanField(default=False)
    notifications_application = models.BooleanField(default=True)
    
    # Types de notifications
    notify_rdv_rappel = models.BooleanField(default=True)
    notify_rdv_annulation = models.BooleanField(default=True)
    notify_rdv_confirmation = models.BooleanField(default=True)
    
    notify_consultation_ajout = models.BooleanField(default=True)
    notify_examen_resultat = models.BooleanField(default=True)
    
    notify_paiement_success = models.BooleanField(default=True)
    notify_paiement_echec = models.BooleanField(default=True)
    notify_abonnement_expiration = models.BooleanField(default=True)
    
    notify_securite_connexion = models.BooleanField(default=True)
    notify_security_changement_mdp = models.BooleanField(default=True)
    
    # Fréquence des rappels
    rappel_rdv_heures = models.IntegerField(default=24)  # Rappel 24h avant
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Préférences {self.utilisateur}"
    
    class Meta:
        db_table = 'preference_notification'
        verbose_name = 'Préférence de notification'
        verbose_name_plural = 'Préférences de notifications'