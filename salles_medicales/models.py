from django.db import models
from gestion_tenants.models import Tenant
from comptes.models import Utilisateur
from rendez_vous.models import RendezVous

class TypeSalle(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

class SalleMedicale(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    type_salle = models.ForeignKey(TypeSalle, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    capacite = models.IntegerField()
    equipements = models.TextField(blank=True)
    statut = models.CharField(max_length=20, default='disponible')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['tenant', 'statut'])]

    def __str__(self):
        return f"{self.nom} ({self.code})"

class ReservationSalle(models.Model):
    STATUT_CHOICES = [
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
        ('terminee', 'Terminée'),
    ]
    salle = models.ForeignKey(SalleMedicale, on_delete=models.CASCADE)
    rendez_vous = models.OneToOneField(RendezVous, on_delete=models.CASCADE, null=True, blank=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    motif = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='confirmee')
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=['salle', 'date_debut'])]
        unique_together = ('salle', 'date_debut')

    def __str__(self):
        return f"{self.salle.nom} - {self.date_debut.strftime('%d/%m %H:%M')}"