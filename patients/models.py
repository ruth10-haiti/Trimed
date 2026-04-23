from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator

class Patient(models.Model):
    """TABLE Patient"""
    
    class Sexe(models.TextChoices):
        M = 'M', 'Masculin'
        F = 'F', 'Féminin'
        AUTRE = 'Autre', 'Autre'
    
    patient_id = models.AutoField(primary_key=True)
    hopital = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='hopital_id',
        null=True, 
        blank=True
    )
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(
        max_length=10,
        choices=Sexe.choices,
        null=True,
        blank=True
    )
    
    numero_dossier_medical = models.CharField(max_length=50, unique=True)
    numero_identification_nationale = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )
    
    telephone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        validators=[EmailValidator()]
    )
    
    cree_le = models.DateTimeField(default=timezone.now)
    modifie_le = models.DateTimeField(auto_now=True)
    utilisateur = models.OneToOneField(
        'comptes.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_lie'
    )
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    class Meta:
        db_table = 'patient'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-cree_le']  # CORRECTION: Ajouter ordering
        indexes = [
            models.Index(fields=['numero_dossier_medical']),
            models.Index(fields=['hopital', 'nom']),
        ]


# Les autres modèles restent identiques
class AdressePatient(models.Model):
    """TABLE AdressePatient"""
    
    adresse_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    
    pays = models.CharField(max_length=100, default='France')
    departement = models.CharField(max_length=100, null=True, blank=True)
    ville = models.CharField(max_length=100)
    adresse_ligne1 = models.CharField(max_length=255)
    adresse_ligne2 = models.CharField(max_length=255, null=True, blank=True)
    code_postal = models.CharField(max_length=20)
    
    cree_le = models.DateTimeField(default=timezone.now)
    modifie_le = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ville} - {self.patient}"
    
    class Meta:
        db_table = 'adresse_patient'
        verbose_name = 'Adresse Patient'
        verbose_name_plural = 'Adresses Patients'


class PersonneAContacter(models.Model):
    """TABLE PersonneAContacter"""
    
    contact_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=50)
    relation = models.CharField(max_length=100, null=True, blank=True)
    cree_le = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.nom} ({self.relation})"
    
    class Meta:
        db_table = 'personne_a_contacter'
        verbose_name = 'Personne à contacter'
        verbose_name_plural = 'Personnes à contacter'


class AssurancePatient(models.Model):
    """TABLE AssurancePatient"""
    
    assurance_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    
    nom_assurance = models.CharField(max_length=255)
    numero_police = models.CharField(max_length=50)
    date_expiration = models.DateField(null=True, blank=True)
    cree_le = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.nom_assurance} - {self.patient}"
    
    class Meta:
        db_table = 'assurance_patient'
        verbose_name = 'Assurance Patient'
        verbose_name_plural = 'Assurances Patients'


class AllergiePatient(models.Model):
    """TABLE AllergiePatient"""
    
    class Gravite(models.TextChoices):
        LEGERE = 'legere', 'Légère'
        MODEREE = 'moderee', 'Modérée'
        SEVERE = 'severe', 'Sévère'
        CRITIQUE = 'critique', 'Critique'
    
    allergie_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    
    nom_allergie = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    gravite = models.CharField(
        max_length=20,
        choices=Gravite.choices,
        default=Gravite.MODEREE
    )
    cree_le = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.nom_allergie} ({self.get_gravite_display()})"
    
    class Meta:
        db_table = 'allergie_patient'
        verbose_name = 'Allergie Patient'
        verbose_name_plural = 'Allergies Patients'


class AntecedentMedical(models.Model):
    """TABLE AntecedentMedical"""
    
    class TypeAntecedent(models.TextChoices):
        MALADIE_CHRONIQUE = 'maladie_chronique', 'Maladie chronique'
        CHIRURGIE = 'chirurgie', 'Chirurgie'
        TRAUMATISME = 'traumatisme', 'Traumatisme'
        ALLERGIE = 'allergie', 'Allergie'
        AUTRE = 'autre', 'Autre'
    
    antecedent_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    
    type_antecedent = models.CharField(
        max_length=50,
        choices=TypeAntecedent.choices,
        default=TypeAntecedent.AUTRE
    )
    description = models.TextField()
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    en_cours = models.BooleanField(default=False)
    cree_le = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.get_type_antecedent_display()} - {self.patient}"
    
    class Meta:
        db_table = 'antecedent_medical'
        verbose_name = 'Antécédent Médical'
        verbose_name_plural = 'Antécédents Médicaux'


class SuiviPatient(models.Model):
    """Suivi médical du patient"""
    
    suivi_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    
    date_suivi = models.DateField()
    
    # Signes vitaux
    poids = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(300)]
    )  # kg
    
    taille = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )  # mètres
    
    tension_arterielle_systolique = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    
    tension_arterielle_diastolique = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(150)]
    )
    
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(45)]
    )  # °C
    
    pouls = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(200)]
    )
    
    frequence_respiratoire = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(8), MaxValueValidator(60)]
    )
    
    glycemie = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(30)]
    )  # mmol/L
    
    # Observations
    observations = models.TextField(null=True, blank=True)
    
    # Relation médicale
    medecin = models.ForeignKey(
        'medical.Medecin',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='medecin_id'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Suivi {self.patient} - {self.date_suivi}"
    
    @property
    def imc(self):
        """Calcul de l'IMC"""
        if self.poids and self.taille:
            try:
                return round(float(self.poids) / (float(self.taille) ** 2), 2)
            except:
                return None
        return None
    
    @property
    def interpretation_imc(self):
        """Interprétation de l'IMC"""
        imc = self.imc
        if not imc:
            return None
        
        if imc < 18.5:
            return "Maigreur"
        elif imc < 25:
            return "Normal"
        elif imc < 30:
            return "Surpoids"
        elif imc < 35:
            return "Obésité modérée"
        elif imc < 40:
            return "Obésité sévère"
        else:
            return "Obésité morbide"
    
    class Meta:
        db_table = 'suivi_patient'
        verbose_name = 'Suivi Patient'
        verbose_name_plural = 'Suivis Patients'
        ordering = ['-date_suivi']