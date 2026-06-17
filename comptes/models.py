from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password, check_password


class GestionnaireUtilisateur(BaseUserManager):
    """Gestionnaire personnalisé pour les utilisateurs"""
    
    def creer_utilisateur(self, email, nom_complet, mot_de_passe=None, **extra_fields):
        """Crée un utilisateur normal"""
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
        """Crée un superutilisateur"""
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
    TABLE Utilisateur - Modèle simplifié
    ✅ Conservation : vérification email via Brevo
    ❌ Suppression : validation de documents (CINU, diplômes, etc.)
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
    is_active = models.BooleanField(default=False)  # ✅ Activé après vérification email
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    
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
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.cree_le = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['hopital']),
        ]


class EmailVerificationToken(models.Model):
    """
    ✅ CONSERVÉ : Token pour vérification email via Brevo
    """
    utilisateur = models.ForeignKey(
        'Utilisateur',
        on_delete=models.CASCADE,
        related_name='verification_tokens'
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        default=timezone.now() + timedelta(hours=24)
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        """Vérifie si le token est encore valide"""
        return not self.verified_at and self.expires_at > timezone.now()
    
    def __str__(self):
        return f"Token pour {self.utilisateur.email}"