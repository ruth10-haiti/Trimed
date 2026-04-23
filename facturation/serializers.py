# serializers.py
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import (
    Plan, AbonnementStatut, PaiementMethode, PaiementStatut,
    InvoiceStatut, Abonnement, Paiement, Invoice,
    AbonnementRenouvellement, EssaiGratuit, Coupon, CouponTenant,
    TarifConsultation
)
from gestion_tenants.serializers import TenantSerializer
from medical.serializers import SpecialiteSerializer

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'
        read_only_fields = ('plan_id', 'created_at', 'updated_at')
    
    def validate_prix_mensuel(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix mensuel doit être positif")
        return value
    
    def validate_prix_annuel(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix annuel doit être positif")
        return value

class AbonnementStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbonnementStatut
        fields = '__all__'
        read_only_fields = ('statut_id',)

class PaiementMethodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaiementMethode
        fields = '__all__'
        read_only_fields = ('methode_id',)

class PaiementStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaiementStatut
        fields = '__all__'
        read_only_fields = ('statut_id',)

class InvoiceStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceStatut
        fields = '__all__'
        read_only_fields = ('statut_id',)

class AbonnementSerializer(serializers.ModelSerializer):
    plan_detail = PlanSerializer(source='plan', read_only=True)
    statut_detail = AbonnementStatutSerializer(source='statut', read_only=True)
    tenant_detail = TenantSerializer(source='tenant', read_only=True)
    
    jours_restants = serializers.ReadOnlyField()
    est_expire = serializers.ReadOnlyField()
    expire_bientot = serializers.ReadOnlyField()
    
    class Meta:
        model = Abonnement
        fields = [
            'abonnement_id', 'tenant', 'tenant_detail', 'plan', 'plan_detail',
            'statut', 'statut_detail', 'date_debut', 'date_fin',
            'jours_restants', 'est_expire', 'expire_bientot',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('abonnement_id', 'created_at', 'updated_at')
    
    def validate_date_fin(self, value):
        date_debut = self.initial_data.get('date_debut')
        if date_debut and value <= date_debut:
            raise serializers.ValidationError("La date de fin doit être après la date de début")
        return value

class PaiementSerializer(serializers.ModelSerializer):
    abonnement_detail = AbonnementSerializer(source='abonnement', read_only=True)
    methode_detail = PaiementMethodeSerializer(source='methode', read_only=True)
    statut_detail = PaiementStatutSerializer(source='statut', read_only=True)
    tenant_detail = TenantSerializer(source='tenant', read_only=True)
    
    class Meta:
        model = Paiement
        fields = [
            'paiement_id', 'tenant', 'tenant_detail', 'abonnement', 'abonnement_detail',
            'methode', 'methode_detail', 'statut', 'statut_detail',
            'montant', 'date_paiement', 'reference', 'notes', 'created_at'
        ]
        read_only_fields = ('paiement_id', 'created_at')
    
    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être positif")
        return value

class InvoiceSerializer(serializers.ModelSerializer):
    paiement_detail = PaiementSerializer(source='paiement', read_only=True)
    statut_detail = InvoiceStatutSerializer(source='statut', read_only=True)
    tenant_detail = TenantSerializer(source='tenant', read_only=True)
    
    est_en_retard = serializers.ReadOnlyField()
    jours_retard = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_id', 'paiement', 'paiement_detail', 'tenant', 'tenant_detail',
            'statut', 'statut_detail', 'numero_facture', 'date_emission',
            'date_echeance', 'montant', 'tva', 'montant_ttc', 'url_pdf',
            'est_en_retard', 'jours_retard', 'created_at', 'updated_at'
        ]
        read_only_fields = ('invoice_id', 'created_at', 'updated_at')
    
    def validate_numero_facture(self, value):
        if Invoice.objects.filter(numero_facture=value).exists():
            raise serializers.ValidationError("Ce numéro de facture existe déjà")
        return value
    
    def validate(self, data):
        # Validation des dates
        if data.get('date_echeance') and data.get('date_emission'):
            if data['date_echeance'] < data['date_emission']:
                raise serializers.ValidationError({
                    'date_echeance': 'La date d\'échéance ne peut pas être antérieure à la date d\'émission'
                })
        
        # Validation des montants
        if data.get('montant_ttc'):
            montant = data.get('montant', Decimal('0.00'))
            tva = data.get('tva', Decimal('0.00'))
            if data['montant_ttc'] != montant + tva:
                raise serializers.ValidationError({
                    'montant_ttc': 'Le montant TTC doit être égal au montant + TVA'
                })
        
        return data

class CouponSerializer(serializers.ModelSerializer):
    plans_valides_list = PlanSerializer(source='plans_valides', many=True, read_only=True)
    est_valide = serializers.ReadOnlyField()
    
    class Meta:
        model = Coupon
        fields = [
            'coupon_id', 'code', 'description', 'type_reduction', 'valeur',
            'date_debut', 'date_fin', 'utilisation_max', 'utilisations_actuelles',
            'plans_valides', 'plans_valides_list', 'actif', 'est_valide',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('coupon_id', 'created_at', 'updated_at', 'utilisations_actuelles')
    
    def validate_code(self, value):
        if Coupon.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ce code de coupon existe déjà")
        return value
    
    def validate_date_fin(self, value):
        date_debut = self.initial_data.get('date_debut')
        if date_debut and value <= date_debut:
            raise serializers.ValidationError("La date de fin doit être après la date de début")
        return value
    
    def validate(self, data):
        # Validation de la valeur selon le type
        if data.get('type_reduction') == 'pourcentage':
            valeur = data.get('valeur')
            if valeur and (valeur <= 0 or valeur > 100):
                raise serializers.ValidationError({
                    'valeur': 'Pour un pourcentage, la valeur doit être entre 0 et 100'
                })
        
        return data

class ValidationCouponSerializer(serializers.Serializer):
    """Serializer pour valider un coupon"""
    
    code = serializers.CharField(required=True)
    plan_id = serializers.IntegerField(required=False)
    montant = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=0
    )
    
    def validate(self, data):
        try:
            coupon = Coupon.objects.get(code=data['code'])
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({
                'code': 'Coupon invalide'
            })
        
        if not coupon.est_valide:
            raise serializers.ValidationError({
                'code': 'Ce coupon n\'est plus valide'
            })
        
        # Vérifier si le coupon est valide pour le plan
        if data.get('plan_id'):
            plan = Plan.objects.get(pk=data['plan_id'])
            if not coupon.plans_valides.filter(pk=plan.pk).exists():
                raise serializers.ValidationError({
                    'code': 'Ce coupon n\'est pas valide pour ce plan'
                })
        
        # Appliquer la réduction
        montant_reduit = coupon.appliquer_reduction(data['montant'])
        
        data['coupon'] = coupon
        data['montant_initial'] = data['montant']
        data['montant_final'] = montant_reduit
        data['reduction'] = data['montant'] - montant_reduit
        
        return data

class TarifConsultationSerializer(serializers.ModelSerializer):
    specialite_detail = SpecialiteSerializer(source='specialite', read_only=True)
    
    class Meta:
        model = TarifConsultation
        fields = [
            'tarif_id', 'tenant', 'specialite', 'specialite_detail',
            'tarif_normal', 'tarif_urgence', 'tarif_nuit', 'tarif_weekend',
            'duree_consultation', 'actif', 'date_debut', 'date_fin',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('tarif_id', 'created_at', 'updated_at')