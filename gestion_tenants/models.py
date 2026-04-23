from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Tenant(models.Model):
    """TABLE Tenant - Établissement hospitalier"""
    
    class StatutVerificationDocument(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        VERIFIE = 'verifie', 'Vérifié'
        REJETE = 'rejete', 'Rejeté'
    
    class Statut(models.TextChoices):
        ACTIF = 'actif', 'Actif'
        INACTIF = 'inactif', 'Inactif'
        SUSPENDU = 'suspendu', 'Suspendu'
    
    class TypeAbonnement(models.TextChoices):
        BASIC = 'basic', 'Basic'
        STANDARD = 'standard', 'Standard'
        PREMIUM = 'premium', 'Premium'
    
    tenant_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    email_professionnel = models.EmailField(max_length=100, blank=True, null=True)
    directeur = models.CharField(max_length=255, blank=True, null=True)
    nombre_de_lits = models.IntegerField(validators=[MinValueValidator(1)])
    numero_enregistrement = models.CharField(max_length=100, blank=True, null=True)
    documents_justificatifs = models.TextField(blank=True, null=True)
    
    statut_verification_document = models.CharField(
        max_length=20,
        choices=StatutVerificationDocument.choices,
        default=StatutVerificationDocument.EN_ATTENTE
    )
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.ACTIF
    )
    type_abonnement = models.CharField(
        max_length=20,
        choices=TypeAbonnement.choices,
        default=TypeAbonnement.BASIC
    )
    
    verifie_par = models.ForeignKey(
        'comptes.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants_verifies'
    )
    date_verification = models.DateTimeField(null=True, blank=True)
    cree_le = models.DateTimeField(default=timezone.now)
    cree_par_utilisateur = models.ForeignKey(
        'comptes.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants_crees'
    )
    proprietaire_utilisateur = models.ForeignKey(
        'comptes.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants_proprietaires'
    )
    nom_schema_base_de_donnees = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = 'tenant'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

class ParametreHopital(models.Model):
    """Paramètres spécifiques à chaque hôpital"""
    
    parametre_id = models.AutoField(primary_key=True)
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    
    fuseau_horaire = models.CharField(max_length=50, default='Europe/Paris')
    langue = models.CharField(max_length=10, default='fr')
    devise = models.CharField(max_length=10, default='EUR')
    
    duree_consultation_defaut = models.IntegerField(default=30)
    notify_rdv_avance = models.BooleanField(default=True)
    notify_rdv_jour = models.BooleanField(default=True)
    
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    tva_taux = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Paramètres {self.tenant.nom}"
    
    class Meta:
        db_table = 'parametre_hopital'
        verbose_name = 'Paramètre Hôpital'
        verbose_name_plural = 'Paramètres Hôpitaux'