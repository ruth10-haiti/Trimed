from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator

class RendezVousType(models.Model):
    """TABLE RendezVousType"""
    
    type_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    duree_defaut = models.IntegerField(default=30)  # en minutes
    couleur = models.CharField(max_length=20, default='#3498db')  # Code couleur
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'rendez_vous_type'
        verbose_name = 'Type de rendez-vous'
        verbose_name_plural = 'Types de rendez-vous'
        unique_together = ['tenant', 'nom']

class RendezVousStatut(models.Model):
    """TABLE RendezVousStatut"""
    
    class CouleurStatut(models.TextChoices):
        SUCCESS = '#2ecc71', 'Vert (Confirmé)'
        WARNING = '#f39c12', 'Orange (En attente)'
        DANGER = '#e74c3c', 'Rouge (Annulé)'
        INFO = '#3498db', 'Bleu (Planifié)'
        SECONDARY = '#95a5a6', 'Gris (Terminé)'
        PRIMARY = '#9b59b6', 'Violet (Reporté)'
    
    statut_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    
    nom = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    couleur = models.CharField(
        max_length=20,
        choices=CouleurStatut.choices,
        default=CouleurStatut.INFO
    )
    est_annule = models.BooleanField(default=False)
    est_confirme = models.BooleanField(default=False)
    est_termine = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'rendez_vous_statut'
        verbose_name = 'Statut de rendez-vous'
        verbose_name_plural = 'Statuts de rendez-vous'
        unique_together = ['tenant', 'nom']

class RendezVous(models.Model):
    """TABLE RendezVous"""
    
    rendez_vous_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    medecin = models.ForeignKey(
        'medical.Medecin',
        on_delete=models.CASCADE,
        db_column='medecin_id'
    )
    
    date_heure = models.DateTimeField()
    
    type = models.ForeignKey(
        RendezVousType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='type_id'
    )
    statut = models.ForeignKey(
        RendezVousStatut,
        on_delete=models.CASCADE,
        db_column='statut_id'
    )
    
    motif = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    raison_annulation = models.TextField(null=True, blank=True)
    
    # Suivi
    rappel_envoye = models.BooleanField(default=False)
    date_rappel = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"RDV {self.patient} - {self.date_heure}"
    
    @property
    def duree(self):
        """Durée du rendez-vous"""
        if self.type:
            return self.type.duree_defaut
        return 30  # Durée par défaut de 30 minutes
    
    @property
    def date_fin(self):
        """Date et heure de fin du rendez-vous"""
        return self.date_heure + timedelta(minutes=self.duree)
    
    @property
    def est_dans_futur(self):
        """Vérifie si le rendez-vous est dans le futur"""
        return self.date_heure > timezone.now()
    
    @property
    def est_dans_passe(self):
        """Vérifie si le rendez-vous est dans le passé"""
        return self.date_heure < timezone.now()
    
    @property
    def est_aujourdhui(self):
        """Vérifie si le rendez-vous est aujourd'hui"""
        return self.date_heure.date() == timezone.now().date()
    
    def verifier_disponibilite(self):
        """Vérifie si le créneau est disponible"""
        conflits = RendezVous.objects.filter(
            tenant=self.tenant,
            medecin=self.medecin,
            statut__est_annule=False,
            date_heure__lt=self.date_fin,
            date_fin__gt=self.date_heure
        ).exclude(pk=self.pk if self.pk else None)
        
        return not conflits.exists()
    
    class Meta:
        db_table = 'rendez_vous'
        verbose_name = 'Rendez-vous'
        verbose_name_plural = 'Rendez-vous'
        ordering = ['date_heure']
        indexes = [
            models.Index(fields=['tenant', 'medecin', 'date_heure']),
            models.Index(fields=['patient', 'date_heure']),
            models.Index(fields=['statut', 'date_heure']),
        ]