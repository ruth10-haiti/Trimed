from rest_framework import serializers
from django.utils import timezone
from .models import (
    Patient, AdressePatient, PersonneAContacter,
    AssurancePatient, AllergiePatient, AntecedentMedical,
    SuiviPatient
)

class AdressePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdressePatient
        fields = '__all__'
        read_only_fields = ['adresse_id', 'cree_le', 'modifie_le']

class PersonneAContacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonneAContacter
        fields = '__all__'
        read_only_fields = ['contact_id', 'cree_le']

class AssurancePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssurancePatient
        fields = '__all__'
        read_only_fields = ['assurance_id', 'cree_le']

class AllergiePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergiePatient
        fields = '__all__'
        read_only_fields = ['allergie_id', 'cree_le']

class AntecedentMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntecedentMedical
        fields = '__all__'
        read_only_fields = ['antecedent_id', 'cree_le']

class SuiviPatientSerializer(serializers.ModelSerializer):
    imc = serializers.ReadOnlyField()
    interpretation_imc = serializers.ReadOnlyField()
    
    class Meta:
        model = SuiviPatient
        fields = '__all__'
        read_only_fields = ['suivi_id', 'created_at', 'updated_at']

class PatientListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des patients"""
    age = serializers.SerializerMethodField()
    
    def get_age(self, obj):
        if obj.date_naissance:
            today = timezone.now().date()
            return today.year - obj.date_naissance.year - (
                (today.month, today.day) < (obj.date_naissance.month, obj.date_naissance.day)
            )
        return None
    
    class Meta:
        model = Patient
        fields = [
            'patient_id', 'nom', 'prenom', 'sexe', 'age',
            'numero_dossier_medical', 'telephone', 'email'
        ]

class PatientSerializer(serializers.ModelSerializer):
    """Serializer complet pour les patients"""
    adresses = AdressePatientSerializer(many=True, read_only=True, source='adressepatient_set')
    contacts = PersonneAContacterSerializer(many=True, read_only=True, source='personneacontacter_set')
    assurances = AssurancePatientSerializer(many=True, read_only=True, source='assurancepatient_set')
    allergies = AllergiePatientSerializer(many=True, read_only=True, source='allergiepatient_set')
    antecedents = AntecedentMedicalSerializer(many=True, read_only=True, source='antecedentmedical_set')
    suivis = SuiviPatientSerializer(many=True, read_only=True, source='suivipatient_set')
    age = serializers.SerializerMethodField()
    
    def get_age(self, obj):
        if obj.date_naissance:
            today = timezone.now().date()
            return today.year - obj.date_naissance.year - (
                (today.month, today.day) < (obj.date_naissance.month, obj.date_naissance.day)
            )
        return None
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'cree_le', 'modifie_le']
    
    def validate_numero_dossier_medical(self, value):
        """Validation du numéro de dossier médical"""
        if Patient.objects.filter(numero_dossier_medical=value).exists():
            raise serializers.ValidationError("Ce numéro de dossier médical existe déjà")
        return value
    
    def validate_email(self, value):
        """Validation de l'email"""
        if value and Patient.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé")
        return value