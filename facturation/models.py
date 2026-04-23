# models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Plan(models.Model):
    """Plan d'abonnement"""
    
    plan_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    prix_mensuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    prix_annuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Limites du plan
    max_utilisateurs = models.IntegerField(default=5)
    max_patients = models.IntegerField(default=100)
    max_stockage = models.IntegerField(default=1024)  # en MB
    support_telephone = models.BooleanField(default=False)
    formation = models.BooleanField(default=False)
    
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'plan'
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'

class AbonnementStatut(models.Model):
    """Statut d'abonnement"""
    
    statut_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'abonnement_statut'
        verbose_name = 'Statut d\'abonnement'
        verbose_name_plural = 'Statuts d\'abonnement'

class PaiementMethode(models.Model):
    """Méthode de paiement"""
    
    methode_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'paiement_methode'
        verbose_name = 'Méthode de paiement'
        verbose_name_plural = 'Méthodes de paiement'

class PaiementStatut(models.Model):
    """Statut de paiement"""
    
    statut_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'paiement_statut'
        verbose_name = 'Statut de paiement'
        verbose_name_plural = 'Statuts de paiement'

class InvoiceStatut(models.Model):
    """Statut de facture"""
    
    statut_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'invoice_statut'
        verbose_name = 'Statut de facture'
        verbose_name_plural = 'Statuts de facture'

class Abonnement(models.Model):
    """TABLE Abonnement"""
    
    abonnement_id = models.AutoField(primary_key=True)
    tenant = models.OneToOneField(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        db_column='plan_id'
    )
    statut = models.ForeignKey(
        AbonnementStatut,
        on_delete=models.CASCADE,
        db_column='statut_id'
    )
    
    date_debut = models.DateField()
    date_fin = models.DateField()
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Abonnement {self.tenant} - {self.plan}"
    
    @property
    def jours_restants(self):
        """Nombre de jours restants avant expiration"""
        aujourdhui = timezone.now().date()
        if self.date_fin < aujourdhui:
            return 0
        return (self.date_fin - aujourdhui).days
    
    @property
    def est_expire(self):
        """Vérifie si l'abonnement est expiré"""
        return self.date_fin < timezone.now().date()
    
    @property
    def expire_bientot(self):
        """Vérifie si l'abonnement expire bientôt (moins de 7 jours)"""
        return 0 < self.jours_restants <= 7
    
    class Meta:
        db_table = 'abonnement'
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'

class Paiement(models.Model):
    """TABLE Paiement"""
    
    paiement_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    abonnement = models.ForeignKey(
        Abonnement,
        on_delete=models.CASCADE,
        db_column='abonnement_id'
    )
    methode = models.ForeignKey(
        PaiementMethode,
        on_delete=models.CASCADE,
        db_column='methode_id'
    )
    statut = models.ForeignKey(
        PaiementStatut,
        on_delete=models.CASCADE,
        db_column='statut_id'
    )
    
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    date_paiement = models.DateTimeField()
    reference = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Paiement {self.reference} - {self.montant}"
    
    class Meta:
        db_table = 'paiement'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

class Invoice(models.Model):
    """TABLE Invoice"""
    
    invoice_id = models.AutoField(primary_key=True)
    paiement = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        db_column='paiement_id'
    )
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    statut = models.ForeignKey(
        InvoiceStatut,
        on_delete=models.CASCADE,
        db_column='statut_id'
    )
    
    numero_facture = models.CharField(max_length=50, unique=True)
    date_emission = models.DateTimeField()
    date_echeance = models.DateTimeField(null=True, blank=True)
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    montant_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    url_pdf = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Facture {self.numero_facture}"
    
    def save(self, *args, **kwargs):
        """Calcul automatique du montant TTC"""
        if not self.montant_ttc:
            self.montant_ttc = self.montant + self.tva
        super().save(*args, **kwargs)
    
    @property
    def est_en_retard(self):
        """Vérifie si la facture est en retard"""
        if self.date_echeance:
            return self.statut.nom != 'payé' and self.date_echeance < timezone.now()
        return False
    
    @property
    def jours_retard(self):
        """Nombre de jours de retard"""
        if self.est_en_retard:
            return (timezone.now() - self.date_echeance).days
        return 0
    
    class Meta:
        db_table = 'invoice'
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'

class AbonnementRenouvellement(models.Model):
    """TABLE AbonnementRenouvellement"""
    
    renouvellement_id = models.AutoField(primary_key=True)
    abonnement = models.ForeignKey(
        Abonnement,
        on_delete=models.CASCADE,
        db_column='abonnement_id'
    )
    paiement = models.ForeignKey(
        Paiement,
        on_delete=models.CASCADE,
        db_column='paiement_id'
    )
    
    date_renouvellement = models.DateTimeField()
    periode_mois = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Renouvellement {self.abonnement} - {self.date_renouvellement.date()}"
    
    class Meta:
        db_table = 'abonnement_renouvellement'
        verbose_name = 'Renouvellement d\'abonnement'
        verbose_name_plural = 'Renouvellements d\'abonnement'

class EssaiGratuit(models.Model):
    """TABLE EssaiGratuit"""
    
    essai_id = models.AutoField(primary_key=True)
    tenant = models.OneToOneField(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        db_column='plan_id'
    )
    
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    actif = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Essai {self.tenant} - {self.plan}"
    
    @property
    def jours_restants(self):
        """Nombre de jours restants dans l'essai"""
        aujourdhui = timezone.now().date()
        if self.date_fin.date() < aujourdhui:
            return 0
        return (self.date_fin.date() - aujourdhui).days
    
    @property
    def est_expire(self):
        """Vérifie si l'essai est expiré"""
        return self.date_fin < timezone.now()
    
    class Meta:
        db_table = 'essai_gratuit'
        verbose_name = 'Essai gratuit'
        verbose_name_plural = 'Essais gratuits'

class Coupon(models.Model):
    """TABLE Coupon"""
    
    class TypeReduction(models.TextChoices):
        POURCENTAGE = 'pourcentage', 'Pourcentage'
        FIXE = 'fixe', 'Fixe'
    
    coupon_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    type_reduction = models.CharField(
        max_length=20,
        choices=TypeReduction.choices
    )
    valeur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    utilisation_max = models.IntegerField(null=True, blank=True)
    utilisations_actuelles = models.IntegerField(default=0)
    
    plans_valides = models.ManyToManyField(Plan, blank=True)
    actif = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.code
    
    @property
    def est_valide(self):
        """Vérifie si le coupon est valide"""
        maintenant = timezone.now()
        return (
            self.actif and
            self.date_debut <= maintenant <= self.date_fin and
            (self.utilisation_max is None or self.utilisations_actuelles < self.utilisation_max)
        )
    
    def appliquer_reduction(self, montant):
        """Applique la réduction au montant"""
        if self.type_reduction == 'pourcentage':
            reduction = montant * (self.valeur / 100)
        else:  # fixe
            reduction = self.valeur
        
        return max(montant - reduction, 0)
    
    class Meta:
        db_table = 'coupon'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

class CouponTenant(models.Model):
    """TABLE CouponTenant"""
    
    coupon_tenant_id = models.AutoField(primary_key=True)
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        db_column='coupon_id'
    )
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    
    date_utilisation = models.DateTimeField()
    montant_avant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    montant_apres = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.coupon} - {self.tenant}"
    
    class Meta:
        db_table = 'coupon_tenant'
        verbose_name = 'Coupon utilisé par tenant'
        verbose_name_plural = 'Coupons utilisés par tenants'
        unique_together = ['coupon', 'tenant']

class TarifConsultation(models.Model):
    """Tarif des consultations"""
    
    tarif_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    specialite = models.ForeignKey(
        'medical.Specialite',
        on_delete=models.CASCADE,
        db_column='specialite_id'
    )
    
    tarif_normal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tarif_urgence = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    tarif_nuit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    tarif_weekend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    duree_consultation = models.IntegerField(default=30)  # minutes
    actif = models.BooleanField(default=True)
    
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Tarif {self.specialite} - {self.tenant}"
    
    def get_tarif(self, est_urgence=False, est_nuit=False, est_weekend=False):
        """Obtenir le tarif selon les conditions"""
        if est_urgence and self.tarif_urgence:
            return self.tarif_urgence
        elif est_nuit and self.tarif_nuit:
            return self.tarif_nuit
        elif est_weekend and self.tarif_weekend:
            return self.tarif_weekend
        else:
            return self.tarif_normal
    
    class Meta:
        db_table = 'tarif_consultation'
        verbose_name = 'Tarif Consultation'
        verbose_name_plural = 'Tarifs Consultation'
        unique_together = ['tenant', 'specialite', 'date_debut']