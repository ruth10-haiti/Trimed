from rest_framework import serializers
from django.utils import timezone
from .models import Medicament, MedicamentCategorie

class MedicamentCategorieSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories de médicaments"""
    nb_medicaments = serializers.SerializerMethodField()
    
    def get_nb_medicaments(self, obj):
        return obj.medicament_set.count()
    
    class Meta:
        model = MedicamentCategorie
        fields = '__all__'
        read_only_fields = ['categorie_id', 'created_at', 'updated_at']

class MedicamentListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des médicaments"""
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    besoin_reapprovisionnement = serializers.ReadOnlyField()
    statut_stock = serializers.SerializerMethodField()
    
    def get_statut_stock(self, obj):
        if obj.stock_actuel <= 0:
            return {'niveau': 'rupture', 'couleur': '#e74c3c', 'message': 'Rupture de stock'}
        elif obj.besoin_reapprovisionnement:
            return {'niveau': 'faible', 'couleur': '#f39c12', 'message': 'Stock faible'}
        else:
            return {'niveau': 'normal', 'couleur': '#2ecc71', 'message': 'Stock normal'}
    
    class Meta:
        model = Medicament
        fields = [
            'medicament_id', 'nom', 'forme_pharmaceutique', 'dosage_standard',
            'categorie_nom', 'stock_actuel', 'stock_minimum', 'prix_unitaire',
            'besoin_reapprovisionnement', 'statut_stock', 'actif'
        ]

class MedicamentSerializer(serializers.ModelSerializer):
    """Serializer complet pour les médicaments"""
    categorie_detail = MedicamentCategorieSerializer(source='categorie', read_only=True)
    besoin_reapprovisionnement = serializers.ReadOnlyField()
    statut_stock = serializers.SerializerMethodField()
    valeur_stock = serializers.SerializerMethodField()
    historique_stock = serializers.SerializerMethodField()
    
    def get_statut_stock(self, obj):
        if obj.stock_actuel <= 0:
            return {'niveau': 'rupture', 'couleur': '#e74c3c', 'message': 'Rupture de stock'}
        elif obj.besoin_reapprovisionnement:
            return {'niveau': 'faible', 'couleur': '#f39c12', 'message': 'Stock faible'}
        else:
            return {'niveau': 'normal', 'couleur': '#2ecc71', 'message': 'Stock normal'}
    
    def get_valeur_stock(self, obj):
        """Calcul de la valeur totale du stock"""
        if obj.prix_unitaire and obj.stock_actuel:
            return float(obj.prix_unitaire) * obj.stock_actuel
        return 0
    
    def get_historique_stock(self, obj):
        """Historique récent des mouvements de stock (simulé)"""
        # Dans une vraie application, ceci viendrait d'un modèle HistoriqueStock
        return []
    
    class Meta:
        model = Medicament
        fields = '__all__'
        read_only_fields = ['medicament_id', 'created_at', 'updated_at']
    
    def validate_stock_minimum(self, value):
        """Validation du stock minimum"""
        if value < 0:
            raise serializers.ValidationError("Le stock minimum ne peut pas être négatif")
        return value
    
    def validate_stock_actuel(self, value):
        """Validation du stock actuel"""
        if value < 0:
            raise serializers.ValidationError("Le stock actuel ne peut pas être négatif")
        return value
    
    def validate_prix_unitaire(self, value):
        """Validation du prix unitaire"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Le prix unitaire ne peut pas être négatif")
        return value

class MedicamentCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de médicaments"""
    class Meta:
        model = Medicament
        fields = [
            'nom', 'forme_pharmaceutique', 'dosage_standard', 'categorie',
            'code_atc', 'dci', 'description', 'stock_actuel', 'stock_minimum',
            'prix_unitaire', 'necessite_ordonnance', 'actif'
        ]
    
    def create(self, validated_data):
        # Ajouter le tenant automatiquement
        validated_data['tenant'] = self.context['request'].user.hopital
        return super().create(validated_data)

class MedicamentStockUpdateSerializer(serializers.Serializer):
    """Serializer pour la mise à jour du stock"""
    TYPES_MOUVEMENT = [
        ('entree', 'Entrée de stock'),
        ('sortie', 'Sortie de stock'),
        ('ajustement', 'Ajustement'),
        ('peremption', 'Péremption'),
    ]
    
    type_mouvement = serializers.ChoiceField(choices=TYPES_MOUVEMENT)
    quantite = serializers.IntegerField(min_value=1)
    motif = serializers.CharField(max_length=255, required=False, allow_blank=True)
    prix_unitaire = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    
    def validate_quantite(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être positive")
        return value

class MedicamentRuptureSerializer(serializers.ModelSerializer):
    """Serializer pour les médicaments en rupture de stock"""
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    jours_rupture = serializers.SerializerMethodField()
    
    def get_jours_rupture(self, obj):
        # Simuler le calcul des jours en rupture
        # Dans une vraie application, ceci viendrait d'un historique
        return 0
    
    class Meta:
        model = Medicament
        fields = [
            'medicament_id', 'nom', 'forme_pharmaceutique', 'categorie_nom',
            'stock_actuel', 'stock_minimum', 'jours_rupture', 'prix_unitaire'
        ]

class MedicamentStatistiquesSerializer(serializers.Serializer):
    """Serializer pour les statistiques des médicaments"""
    total_medicaments = serializers.IntegerField()
    medicaments_actifs = serializers.IntegerField()
    medicaments_rupture = serializers.IntegerField()
    medicaments_stock_faible = serializers.IntegerField()
    valeur_stock_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    categories_count = serializers.IntegerField()
    
    # Répartition par forme pharmaceutique
    repartition_formes = serializers.DictField()
    
    # Top 10 des médicaments les plus chers
    top_medicaments_chers = serializers.ListField()
    
    # Médicaments nécessitant une attention
    attention_requise = serializers.ListField()

class MedicamentRechercheSerializer(serializers.Serializer):
    """Serializer pour la recherche avancée de médicaments"""
    nom = serializers.CharField(required=False, allow_blank=True)
    forme_pharmaceutique = serializers.CharField(required=False, allow_blank=True)
    categorie = serializers.IntegerField(required=False, allow_null=True)
    code_atc = serializers.CharField(required=False, allow_blank=True)
    dci = serializers.CharField(required=False, allow_blank=True)
    necessite_ordonnance = serializers.BooleanField(required=False, allow_null=True)
    stock_minimum_atteint = serializers.BooleanField(required=False, allow_null=True)
    actif = serializers.BooleanField(required=False, allow_null=True)
    prix_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    prix_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)