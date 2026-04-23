from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator

class GroupeSanguin(models.Model):
    """TABLE GroupeSanguin"""
    
    class CodeGroupe(models.TextChoices):
        A_POSITIF = 'A+', 'A+'
        A_NEGATIF = 'A-', 'A-'
        B_POSITIF = 'B+', 'B+'
        B_NEGATIF = 'B-', 'B-'
        AB_POSITIF = 'AB+', 'AB+'
        AB_NEGATIF = 'AB-', 'AB-'
        O_POSITIF = 'O+', 'O+'
        O_NEGATIF = 'O-', 'O-'
    
    groupe_id = models.AutoField(primary_key=True)
    code = models.CharField(
        max_length=3,
        choices=CodeGroupe.choices,
        unique=True
    )
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.code
    
    class Meta:
        db_table = 'groupe_sanguin'
        verbose_name = 'Groupe Sanguin'
        verbose_name_plural = 'Groupes Sanguins'

class Specialite(models.Model):
    """TABLE Specialite"""
    
    specialite_id = models.AutoField(primary_key=True)
    nom_specialite = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nom_specialite
    
    class Meta:
        db_table = 'specialite'
        verbose_name = 'Spécialité'
        verbose_name_plural = 'Spécialités'
        ordering = ['nom_specialite']

class Medecin(models.Model):
    """TABLE Medecin"""
    
    class Sexe(models.TextChoices):
        M = 'M', 'Masculin'
        F = 'F', 'Féminin'
        AUTRE = 'Autre', 'Autre'
    
    medecin_id = models.AutoField(primary_key=True)
    hopital = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='hopital_id'
    )
    specialite_principale = models.ForeignKey(
        Specialite,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='specialite_principale_id'
    )
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(
        max_length=10,
        choices=Sexe.choices,
        null=True,
        blank=True
    )
    date_naissance = models.DateField(null=True, blank=True)
    
    telephone = models.CharField(max_length=50, null=True, blank=True)
    email_professionnel = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        validators=[EmailValidator()]
    )
    
    numero_identification = models.CharField(max_length=50, null=True, blank=True)
    numero_matricule_professionnel = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    
    cree_le = models.DateTimeField(default=timezone.now)
    modifie_le = models.DateTimeField(auto_now=True)
    cree_par_utilisateur = models.ForeignKey(
        'comptes.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medecins_crees',
        db_column='cree_par_utilisateur_id'
    )
    modifie_par_utilisateur = models.ForeignKey(
        'comptes.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medecins_modifies',
        db_column='modifie_par_utilisateur_id'
    )
    utilisateur = models.OneToOneField(
        'comptes.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medecin_lie'
    )
    
    def __str__(self):
        return f"Dr {self.prenom} {self.nom}"
    
    class Meta:
        db_table = 'medecin'
        verbose_name = 'Médecin'
        verbose_name_plural = 'Médecins'
        indexes = [
            models.Index(fields=['hopital', 'nom']),
            models.Index(fields=['specialite_principale']),
        ]

class Consultation(models.Model):
    """TABLE Consultation"""
    
    consultation_id = models.AutoField(primary_key=True)
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
        Medecin,
        on_delete=models.CASCADE,
        db_column='medecin_id'
    )
    rendez_vous = models.ForeignKey(
        'rendez_vous.RendezVous',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='rendez_vous_id'
    )
    
    date_consultation = models.DateTimeField()
    motif = models.CharField(max_length=255)
    diagnostic_principal = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Consultation {self.patient} - {self.date_consultation.date()}"
    
    class Meta:
        db_table = 'consultation'
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
        ordering = ['-date_consultation']
        indexes = [
            models.Index(fields=['tenant', 'patient']),
            models.Index(fields=['medecin', 'date_consultation']),
        ]

class Ordonnance(models.Model):
    """TABLE Ordonnance"""
    
    ordonnance_id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        'gestion_tenants.Tenant',
        on_delete=models.CASCADE,
        db_column='tenant_id'
    )
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        db_column='consultation_id'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        db_column='patient_id'
    )
    medecin = models.ForeignKey(
        Medecin,
        on_delete=models.CASCADE,
        db_column='medecin_id'
    )
    
    date_ordonnance = models.DateTimeField()
    recommandations = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Ordonnance {self.patient} - {self.date_ordonnance.date()}"
    
    class Meta:
        db_table = 'ordonnance'
        verbose_name = 'Ordonnance'
        verbose_name_plural = 'Ordonnances'
        ordering = ['-date_ordonnance']

class ExamenMedical(models.Model):
    """TABLE ExamenMedical"""
    
    class TypeExamen(models.TextChoices):
        BIOLOGIE = 'biologie', 'Biologie'
        IMAGERIE = 'imagerie', 'Imagerie'
        ELECTROCARDIOGRAMME = 'ecg', 'Électrocardiogramme'
        RADIOLOGIE = 'radiologie', 'Radiologie'
        SCANNER = 'scanner', 'Scanner'
        IRM = 'irm', 'IRM'
        ECHOGRAPHIE = 'echographie', 'Échographie'
        ENDOSCOPIE = 'endoscopie', 'Endoscopie'
        AUTRE = 'autre', 'Autre'
    
    examen_id = models.AutoField(primary_key=True)
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
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='consultation_id'
    )
    medecin_prescripteur = models.ForeignKey(
        Medecin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='examens_prescrits',
        db_column='medecin_prescripteur_id'
    )
    
    nom_examen = models.CharField(max_length=255)
    type_examen = models.CharField(
        max_length=50,
        choices=TypeExamen.choices,
        default=TypeExamen.BIOLOGIE
    )
    resultat = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    fichier_resultat = models.FileField(
        upload_to='examens/',
        null=True,
        blank=True,
        max_length=255
    )
    
    date_examen = models.DateTimeField()
    date_resultat = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Examen {self.nom_examen} - {self.patient}"
    
    class Meta:
        db_table = 'examen_medical'
        verbose_name = 'Examen Médical'
        verbose_name_plural = 'Examens Médicaux'
        ordering = ['-date_examen']

class Prescription(models.Model):
    """Prescription de médicaments dans une ordonnance"""
    
    prescription_id = models.AutoField(primary_key=True)
    ordonnance = models.ForeignKey(
        Ordonnance,
        on_delete=models.CASCADE,
        db_column='ordonnance_id'
    )
    medicament = models.ForeignKey(
        'gestion_medicaments.Medicament',
        on_delete=models.CASCADE,
        db_column='medicament_id'
    )
    
    dosage = models.CharField(max_length=100)
    frequence = models.CharField(max_length=100)
    duree = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField(default=1)
    instructions = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription {self.medicament.nom} - {self.ordonnance}"
    
    class Meta:
        db_table = 'prescription'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        unique_together = ['ordonnance', 'medicament']

class LignePrescription(models.Model):
    """Détail d'une ligne de prescription"""
    
    ligne_id = models.AutoField(primary_key=True)
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        db_column='prescription_id'
    )
    
    medicament_nom = models.CharField(max_length=150)
    forme_pharmaceutique = models.CharField(max_length=100)
    posologie = models.CharField(max_length=255)
    duree_traitement = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.medicament_nom} - {self.prescription}"
    
    class Meta:
        db_table = 'ligne_prescription'
        verbose_name = 'Ligne de Prescription'
        verbose_name_plural = 'Lignes de Prescription'