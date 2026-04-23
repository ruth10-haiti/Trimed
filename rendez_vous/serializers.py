from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from .models import RendezVous, RendezVousType, RendezVousStatut

class RendezVousTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVousType
        fields = '__all__'
        read_only_fields = ['type_id', 'created_at', 'updated_at']

class RendezVousStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVousStatut
        fields = '__all__'
        read_only_fields = ['statut_id', 'created_at', 'updated_at']

class RendezVousListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des rendez-vous"""
    patient_nom = serializers.CharField(source='patient.nom', read_only=True)
    patient_prenom = serializers.CharField(source='patient.prenom', read_only=True)
    medecin_nom = serializers.CharField(source='medecin.nom', read_only=True)
    medecin_prenom = serializers.CharField(source='medecin.prenom', read_only=True)
    type_nom = serializers.CharField(source='type.nom', read_only=True)
    statut_nom = serializers.CharField(source='statut.nom', read_only=True)
    statut_couleur = serializers.CharField(source='statut.couleur', read_only=True)
    duree = serializers.ReadOnlyField()
    date_fin = serializers.ReadOnlyField()
    
    class Meta:
        model = RendezVous
        fields = [
            'rendez_vous_id', 'date_heure', 'motif', 'notes',
            'patient_nom', 'patient_prenom', 'medecin_nom', 'medecin_prenom',
            'type_nom', 'statut_nom', 'statut_couleur', 'duree', 'date_fin'
        ]

class RendezVousSerializer(serializers.ModelSerializer):
    """Serializer complet pour les rendez-vous"""
    patient_detail = serializers.SerializerMethodField()
    medecin_detail = serializers.SerializerMethodField()
    type_detail = RendezVousTypeSerializer(source='type', read_only=True)
    statut_detail = RendezVousStatutSerializer(source='statut', read_only=True)
    duree = serializers.ReadOnlyField()
    date_fin = serializers.ReadOnlyField()
    est_dans_futur = serializers.ReadOnlyField()
    est_dans_passe = serializers.ReadOnlyField()
    est_aujourdhui = serializers.ReadOnlyField()
    
    def get_patient_detail(self, obj):
        if obj.patient:
            return {
                'patient_id': obj.patient.patient_id,
                'nom': obj.patient.nom,
                'prenom': obj.patient.prenom,
                'telephone': obj.patient.telephone,
                'email': obj.patient.email
            }
        return None
    
    def get_medecin_detail(self, obj):
        if obj.medecin:
            return {
                'medecin_id': obj.medecin.medecin_id,
                'nom': obj.medecin.nom,
                'prenom': obj.medecin.prenom,
                'specialite': obj.medecin.specialite_principale.nom_specialite if obj.medecin.specialite_principale else None
            }
        return None
    
    class Meta:
        model = RendezVous
        fields = '__all__'
        read_only_fields = ['rendez_vous_id', 'created_at', 'updated_at']
    
    def validate_date_heure(self, value):
        """Validation de la date et heure du rendez-vous"""
        # Vérifier que la date n'est pas dans le passé
        if value < timezone.now():
            raise serializers.ValidationError("La date du rendez-vous ne peut pas être dans le passé")
        
        # Vérifier les heures d'ouverture (8h-18h)
        if value.hour < 8 or value.hour >= 18:
            raise serializers.ValidationError("Les rendez-vous doivent être entre 8h et 18h")
        
        # Vérifier que ce n'est pas un dimanche
        if value.weekday() == 6:  # 6 = dimanche
            raise serializers.ValidationError("Pas de rendez-vous le dimanche")
        
        return value
    
    def validate(self, data):
        """Validation globale du rendez-vous"""
        # Vérifier la disponibilité du médecin
        if 'medecin' in data and 'date_heure' in data:
            medecin = data['medecin']
            date_heure = data['date_heure']
            
            # Calculer la durée du RDV
            duree = 30  # durée par défaut
            if 'type' in data and data['type']:
                duree = data['type'].duree_defaut
            
            date_fin = date_heure + timedelta(minutes=duree)
            
            # Vérifier les conflits
            conflits = RendezVous.objects.filter(
                medecin=medecin,
                statut__est_annule=False,
                date_heure__lt=date_fin,
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            # Vérifier si il y a chevauchement
            for rdv in conflits:
                rdv_fin = rdv.date_heure + timedelta(minutes=rdv.duree)
                if date_heure < rdv_fin:
                    raise serializers.ValidationError(
                        f"Conflit avec un autre rendez-vous de {rdv.date_heure.strftime('%H:%M')} à {rdv_fin.strftime('%H:%M')}"
                    )
        
        return data

class CreneauDisponibleSerializer(serializers.Serializer):
    """Serializer pour les créneaux disponibles"""
    date = serializers.DateField()
    heure_debut = serializers.TimeField()
    heure_fin = serializers.TimeField()
    disponible = serializers.BooleanField()
    duree = serializers.IntegerField()

class RendezVousCreateSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field='nom', queryset=RendezVousType.objects.all())
    statut = serializers.SlugRelatedField(slug_field='nom', queryset=RendezVousStatut.objects.all(), required=False)

    class Meta:
        model = RendezVous
        fields = ['patient', 'medecin', 'date_heure', 'type', 'statut', 'motif', 'notes']

    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].user.hopital
        if 'statut' not in validated_data:
            # Valeur par défaut si non fourni
            statut_defaut, _ = RendezVousStatut.objects.get_or_create(
                tenant=validated_data['tenant'],
                nom='Planifié',
                defaults={'couleur': '#3498db', 'est_confirme': False}
            )
            validated_data['statut'] = statut_defaut
        return super().create(validated_data)