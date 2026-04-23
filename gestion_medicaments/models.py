# models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class MedicamentCategorie(models.Model):
    """TABLE MedicamentCategorie"""
    
    categorie_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'medicament_categorie'
        verbose_name = 'Catégorie de médicament'
        verbose_name_plural = 'Catégories de médicaments'
        unique_together = ['tenant', 'nom']

class Medicament(models.Model):
    """TABLE Medicament"""
    
    class FormePharmaceutique(models.TextChoices):
        COMPRIME = 'comprime', 'Comprimé'
        CAPSULE = 'capsule', 'Capsule'
        SIROP = 'sirop', 'Sirop'
        SUSPENSION = 'suspension', 'Suspension'
        POUDRE = 'poudre', 'Poudre'
        CREME = 'creme', 'Crème'
        POMMADE = 'pommade', 'Pommade'
        GEL = 'gel', 'Gel'
        SOLUTION = 'solution', 'Solution'
        INJECTABLE = 'injectable', 'Injectable'
        SUPPOSITOIRE = 'suppositoire', 'Suppositoire'
        PATCH = 'patch', 'Patch'
        AEROSOL = 'aerosol', 'Aérosol'
        AUTRE = 'autre', 'Autre'
    
    medicament_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    
    nom = models.CharField(max_length=150)
    forme_pharmaceutique = models.CharField(
        max_length=50,
        choices=FormePharmaceutique.choices,
        default=FormePharmaceutique.COMPRIME
    )
    dosage_standard = models.CharField(max_length=100, null=True, blank=True)
    
    categorie = models.ForeignKey(
        MedicamentCategorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='categorie_id'
    )
    
    code_atc = models.CharField(max_length=20, null=True, blank=True)  # Code ATC
    dci = models.CharField(max_length=150, null=True, blank=True)  # Dénomination Commune Internationale
    
    description = models.TextField(null=True, blank=True)
    
    stock_actuel = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimum = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    necessite_ordonnance = models.BooleanField(default=True)
    actif = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    @property
    def besoin_reapprovisionnement(self):
        """Indique si le médicament a besoin d'être réapprovisionné"""
        return self.stock_actuel <= self.stock_minimum
    
    class Meta:
        db_table = 'medicament'
        verbose_name = 'Médicament'
        verbose_name_plural = 'Médicaments'
        indexes = [
            models.Index(fields=['tenant', 'nom']),
            models.Index(fields=['categorie']),
            models.Index(fields=['actif']),
        ]