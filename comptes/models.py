from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password, check_password
import hashlib

class GestionnaireUtilisateur(BaseUserManager):
    """Gestionnaire personnalisé pour les utilisateurs"""
    
    def creer_utilisateur(self, email, nom_complet, mot_de_passe=None, **extra_fields):
        """Crée un utilisateur normal (méthode en français)"""
        if not email:
            raise ValueError('L\'email est obligatoire')
        
        email = self.normalize_email(email)
        utilisateur = self.model(
            email=email,
            nom_complet=nom_complet,
            **extra_fields
        )
        
        if mot_de_passe:
            utilisateur.mot_de_passe = make_password(mot_de_passe)
        else:
            utilisateur.mot_de_passe = make_password(None)
            
        utilisateur.save(using=self._db)
        return utilisateur
    
    def creer_superutilisateur(self, email, nom_complet, mot_de_passe=None, **extra_fields):
        """Crée un superutilisateur (méthode en français)"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin-systeme')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        
        return self.creer_utilisateur(email, nom_complet, mot_de_passe, **extra_fields)
    
    def create_user(self, email, nom_complet, password=None, **extra_fields):
        """Alias pour creer_utilisateur (requis par Django)"""
        return self.creer_utilisateur(email, nom_complet, password, **extra_fields)
    
    def create_superuser(self, email, nom_complet, password=None, **extra_fields):
        """Alias pour creer_superutilisateur (requis par Django)"""
        return self.creer_superutilisateur(email, nom_complet, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """
    TABLE Utilisateur - Modèle personnalisé avec validation documents
    """
    
    class Role(models.TextChoices):
        ADMIN_SYSTEME = 'admin-systeme', 'Administrateur Système'
        PROPRIETAIRE_HOPITAL = 'proprietaire-hopital', 'Propriétaire Hôpital'
        MEDECIN = 'medecin', 'Médecin'
        INFIRMIER = 'infirmier', 'Infirmier'
        SECRETAIRE = 'secretaire', 'Secrétaire'
        PERSONNEL = 'personnel', 'Personnel'
        PATIENT = 'patient', 'Patient'
    
    utilisateur_id = models.AutoField(primary_key=True)
    nom_complet = models.CharField(max_length=255)
    email = models.EmailField(
        max_length=100,
        unique=True,
        validators=[EmailValidator()]
    )
    mot_de_passe = models.CharField(max_length=255, editable=False)
    
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.PATIENT
    )
    
    hopital = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='hopital_id',
        related_name='utilisateurs'
    )
    
    cree_le = models.DateTimeField(default=timezone.now)
    
    # Champs Django requis
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    
    # NOUVEAUX CHAMPS POUR VALIDATION DOCUMENTS
    est_verifie = models.BooleanField(default=False)  # Validation admin complète
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='validations')
    
    # CINU
    ninu = models.CharField(max_length=20, unique=True, null=True, blank=True)
    ninu_hash = models.CharField(max_length=64, null=True, blank=True)
    version_cinu = models.CharField(max_length=5, default='V1')
    qr_code_data = models.JSONField(null=True, blank=True)
    
    # Statuts documents
    statut_cinu = models.CharField(max_length=20, default='PENDING')
    statut_diplome = models.CharField(max_length=20, default='PENDING')
    statut_carte_pro = models.CharField(max_length=20, default='PENDING')
    
    # Relations
    derniere_modification = models.DateTimeField(auto_now=True)
    modifie_par = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs_modifies'
    )

    @property
    def id(self):
        return self.utilisateur_id
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet']
    
    objects = GestionnaireUtilisateur()
    
    def __str__(self):
        return f"{self.nom_complet} ({self.get_role_display()})"
    
    def set_password(self, raw_password):
        """Surcharge pour utiliser le champ mot_de_passe"""
        self.mot_de_passe = make_password(raw_password)
        self._password = raw_password
    
    def check_password(self, raw_password):
        """Surcharge pour utiliser le champ mot_de_passe"""
        return check_password(raw_password, self.mot_de_passe)
    
    def sauvegarder_hash_ninu(self):
        if self.ninu:
            self.ninu_hash = hashlib.sha256(self.ninu.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.cree_le = timezone.now()
        self.sauvegarder_hash_ninu()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['hopital']),
            models.Index(fields=['ninu_hash']),
            models.Index(fields=['statut_cinu']),
        ]


class EmailVerificationToken(models.Model):
    """Token pour vérification email"""
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(hours=24))
    verified_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return not self.verified_at and self.expires_at > timezone.now()
    
    def __str__(self):
        return f"Token pour {self.utilisateur.email}"


class Document(models.Model):
    """Modèle pour les documents uploadés"""
    TYPE_CHOICES = [
        ('CINU', 'Carte d\'Identité Nationale'),
        ('DIPLOME', 'Diplôme'),
        ('CARTE_PRO', 'Carte Professionnelle'),
    ]
    
    STATUT_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
        ('ANALYZING', 'En analyse'),
    ]
    
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=20, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='documents/%Y/%m/%d/')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PENDING')
    
    # Métadonnées fichier
    nom_fichier_original = models.CharField(max_length=255)
    taille_fichier = models.IntegerField()
    type_mime = models.CharField(max_length=100, default='application/pdf')
    
    # Résultats analyse automatique
    hash_document = models.CharField(max_length=64, null=True, blank=True)
    score_confiance = models.IntegerField(default=0)
    analyse_resultats = models.JSONField(default=dict)
    
    # Validation admin
    valide_par = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, related_name='documents_valides')
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True)
    motif_rejet = models.CharField(max_length=500, blank=True)
    
    date_upload = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.get_type_document_display()}"
    
    class Meta:
        db_table = 'document'
        indexes = [
            models.Index(fields=['utilisateur', 'type_document']),
            models.Index(fields=['statut']),
            models.Index(fields=['hash_document']),
        ]


class DocumentBlacklist(models.Model):
    """Anti-doublon - Hash des documents déjà utilisés"""
    hash_document = models.CharField(max_length=64, unique=True)
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    type_document = models.CharField(max_length=50)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_blacklist'
        indexes = [
            models.Index(fields=['hash_document']),
        ]


class CINUBlacklist(models.Model):
    """Anti-doublon - CINU déjà utilisées"""
    ninu_hash = models.CharField(max_length=64, unique=True)
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    date_utilisation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cinu_blacklist'
        indexes = [
            models.Index(fields=['ninu_hash']),
        ]


class VerificationLog(models.Model):
    """Log détaillé des vérifications"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    admin = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, related_name='verifications')
    
    # Résultats analyse
    metadata = models.JSONField(default=dict)
    texte_extrait = models.TextField(blank=True)
    informations_extraites = models.JSONField(default=dict)
    qualite_image = models.JSONField(default=dict)
    detection_falsification = models.JSONField(default=dict)
    
    # Décision
    decision = models.CharField(max_length=20, default='PENDING')
    commentaire_admin = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    date_verification = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'verification_log'
        ordering = ['-date_verification']