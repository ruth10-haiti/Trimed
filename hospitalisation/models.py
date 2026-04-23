from django.db import models
from django.core.validators import MinValueValidator
from gestion_tenants.models import Tenant
from patients.models import Patient

class Chambre(models.Model):
    TYPE_CHOICES = [
        ('privee', 'Privée'),
        ('semi_privee', 'Semi-privée'),
        ('collective', 'Collective'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    numero = models.CharField(max_length=10, unique=True)
    etage = models.IntegerField(validators=[MinValueValidator(0)])
    type_chambre = models.CharField(max_length=20, choices=TYPE_CHOICES)
    capacite = models.IntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, default='libre')  # libre, occupe, maintenance
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['tenant', 'statut'])]

    def __str__(self):
        return f"Chambre {self.numero} ({self.get_type_chambre_display()})"


class Lit(models.Model):
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name='lits')
    numero_lit = models.CharField(max_length=5)
    statut = models.CharField(max_length=20, default='libre')  # libre, occupe, reserve, maintenance

    class Meta:
        unique_together = ('chambre', 'numero_lit')
        indexes = [models.Index(fields=['statut'])]

    def __str__(self):
        return f"Lit {self.numero_lit} - {self.chambre.numero}"


class Admission(models.Model):
    STATUT_CHOICES = [
        ('hospitalise', 'Hospitalisé'),
        ('sorti', 'Sorti'),
        ('transfere', 'Transféré'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    lit = models.ForeignKey(Lit, on_delete=models.CASCADE)
    date_admission = models.DateTimeField(auto_now_add=True)
    date_sortie = models.DateTimeField(null=True, blank=True)
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='hospitalise')
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=['date_admission', 'statut'])]

    def __str__(self):
        return f"{self.patient} - {self.lit} (admis le {self.date_admission.date()})"