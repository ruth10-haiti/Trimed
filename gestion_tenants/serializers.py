# gestion_tenants/serializers.py
from rest_framework import serializers
from .models import Tenant, ParametreHopital

# IMPORTANT: Ne pas importer UtilisateurSerializer pour éviter la récursion
# On va créer un sérializer simple pour le propriétaire


class SimpleProprietaireSerializer(serializers.Serializer):
    """Sérializer simple pour le propriétaire sans récursion"""
    utilisateur_id = serializers.IntegerField(source='utilisateur_id')
    nom_complet = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    
    class Meta:
        fields = ['utilisateur_id', 'nom_complet', 'email', 'role']


class ParametreHopitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametreHopital
        fields = [
            'parametre_id', 'tenant', 'fuseau_horaire', 'langue', 'devise',
            'duree_consultation_defaut', 'notify_rdv_avance', 'notify_rdv_jour',
            'email_notifications', 'sms_notifications', 'tva_taux',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('parametre_id', 'created_at', 'updated_at')


class TenantSerializer(serializers.ModelSerializer):
    # CORRECTION: Utiliser un sérializer simple pour éviter la récursion
    proprietaire_utilisateur = serializers.SerializerMethodField()
    proprietaire_utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=Tenant._meta.get_field('proprietaire_utilisateur').remote_field.model.objects.all(),
        source='proprietaire_utilisateur',
        write_only=True,
        required=False
    )
    parametres = ParametreHopitalSerializer(read_only=True)
    
    def get_proprietaire_utilisateur(self, obj):
        """Retourner les infos du propriétaire sans récursion"""
        if obj.proprietaire_utilisateur:
            return {
                'utilisateur_id': obj.proprietaire_utilisateur.utilisateur_id,
                'nom_complet': obj.proprietaire_utilisateur.nom_complet,
                'email': obj.proprietaire_utilisateur.email,
                'role': obj.proprietaire_utilisateur.role,
            }
        return None
    
    class Meta:
        model = Tenant
        fields = [
            'tenant_id', 'nom', 'adresse', 'telephone', 'email_professionnel',
            'directeur', 'nombre_de_lits', 'numero_enregistrement',
            'documents_justificatifs', 'statut_verification_document',
            'statut', 'type_abonnement', 'verifie_par', 'date_verification',
            'cree_le', 'cree_par_utilisateur', 'proprietaire_utilisateur',
            'proprietaire_utilisateur_id', 'nom_schema_base_de_donnees',
            'parametres'
        ]
        read_only_fields = ('tenant_id', 'cree_le', 'date_verification')
    
    def validate(self, data):
        """Validation personnalisée"""
        if data.get('nombre_de_lits', 0) <= 0:
            raise serializers.ValidationError({
                'nombre_de_lits': 'Le nombre de lits doit être supérieur à 0'
            })
        return data