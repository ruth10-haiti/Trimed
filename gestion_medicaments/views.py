# gestion_medicaments/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from django.db import models
from datetime import datetime, timedelta
from .models import Medicament, MedicamentCategorie
from .serializers import (
    MedicamentSerializer, MedicamentListSerializer, MedicamentCreateSerializer,
    MedicamentCategorieSerializer, MedicamentStockUpdateSerializer,
    MedicamentRuptureSerializer, MedicamentStatistiquesSerializer,
    MedicamentRechercheSerializer
)
from comptes.permissions import (
    EstAdminSysteme, EstProprietaireHopital, EstMedecin, 
    EstPersonnel, PeutGererMedicaments, PeutModifierStock
)

class MedicamentCategorieViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories de médicaments"""
    queryset = MedicamentCategorie.objects.all()
    serializer_class = MedicamentCategorieSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'created_at']
    ordering = ['nom']
    
    def get_permissions(self):
        """Permissions personnalisées selon l'action"""
        # CORRECTION: Admin système et propriétaire peuvent tout faire
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin système voit tout
        if user.role == 'admin-systeme':
            return queryset
        
        # Les autres voient seulement leur tenant
        if user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.hopital)


class MedicamentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les médicaments"""
    queryset = Medicament.objects.all()
    serializer_class = MedicamentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categorie', 'forme_pharmaceutique', 'necessite_ordonnance', 'actif']
    search_fields = ['nom', 'dci', 'code_atc', 'description']
    ordering_fields = ['nom', 'stock_actuel', 'prix_unitaire', 'created_at']
    ordering = ['nom']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MedicamentListSerializer
        elif self.action == 'create':
            return MedicamentCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Permissions personnalisées selon l'action
        """
        # Actions en lecture : tout le monde peut voir
        if self.action in ['list', 'retrieve', 'stock_faible', 'rupture_stock', 'statistiques', 'recherche_avancee', 'export_stock']:
            permission_classes = [IsAuthenticated]
        
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital | EstMedecin]
        
        # CORRECTION: Modification du stock : admin, propriétaire et médecin
        elif self.action == 'mettre_a_jour_stock':
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital | EstMedecin]
        
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin système voit tout
        if user.role == 'admin-systeme':
            return queryset
        
        # Les autres voient seulement leur tenant
        if user.hopital:
            queryset = queryset.filter(tenant=user.hopital)
        
        # Filtres spéciaux
        stock_faible = self.request.query_params.get('stock_faible', None)
        if stock_faible == 'true':
            queryset = queryset.filter(stock_actuel__lte=models.F('stock_minimum'))
        
        rupture = self.request.query_params.get('rupture', None)
        if rupture == 'true':
            queryset = queryset.filter(stock_actuel=0)
        
        prix_min = self.request.query_params.get('prix_min', None)
        prix_max = self.request.query_params.get('prix_max', None)
        
        if prix_min:
            try:
                queryset = queryset.filter(prix_unitaire__gte=float(prix_min))
            except ValueError:
                pass
        
        if prix_max:
            try:
                queryset = queryset.filter(prix_unitaire__lte=float(prix_max))
            except ValueError:
                pass
        
        return queryset.select_related('categorie')
    
    def perform_create(self, serializer):
        """Création d'un médicament"""
        # CORRECTION: Admin système et propriétaire peuvent créer
        user = self.request.user
        if user.role in ['admin-systeme', 'proprietaire-hopital']:
            serializer.save(tenant=user.hopital)
        else:
            serializer.save(tenant=user.hopital)
    
    @action(detail=True, methods=['post'])
    def mettre_a_jour_stock(self, request, pk=None):
        """Mettre à jour le stock d'un médicament"""
        medicament = self.get_object()
        
        # CORRECTION: Vérifier les permissions
        if request.user.role not in ['admin-systeme', 'proprietaire-hopital', 'medecin']:
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier le stock'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MedicamentStockUpdateSerializer(data=request.data)
        if serializer.is_valid():
            type_mouvement = serializer.validated_data['type_mouvement']
            quantite = serializer.validated_data['quantite']
            motif = serializer.validated_data.get('motif', '')
            nouveau_prix = serializer.validated_data.get('prix_unitaire')
            
            # Calculer le nouveau stock
            if type_mouvement == 'entree':
                nouveau_stock = medicament.stock_actuel + quantite
            elif type_mouvement == 'sortie':
                nouveau_stock = max(0, medicament.stock_actuel - quantite)
            elif type_mouvement == 'ajustement':
                nouveau_stock = quantite  # Ajustement direct
            elif type_mouvement == 'peremption':
                nouveau_stock = max(0, medicament.stock_actuel - quantite)
            else:
                return Response(
                    {'error': 'Type de mouvement invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mettre à jour le médicament
            ancien_stock = medicament.stock_actuel
            medicament.stock_actuel = nouveau_stock
            
            if nouveau_prix:
                medicament.prix_unitaire = nouveau_prix
            
            medicament.save()
            
            return Response({
                'message': f'Stock mis à jour: {ancien_stock} → {nouveau_stock}',
                'ancien_stock': ancien_stock,
                'nouveau_stock': nouveau_stock,
                'type_mouvement': type_mouvement,
                'quantite': quantite,
                'motif': motif,
                'medicament': MedicamentSerializer(medicament).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stock_faible(self, request):
        """Récupérer les médicaments avec un stock faible"""
        queryset = self.get_queryset().filter(
            stock_actuel__lte=models.F('stock_minimum'),
            actif=True
        ).order_by('stock_actuel')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MedicamentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MedicamentListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def rupture_stock(self, request):
        """Récupérer les médicaments en rupture de stock"""
        queryset = self.get_queryset().filter(
            stock_actuel=0,
            actif=True
        ).order_by('nom')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MedicamentRuptureSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MedicamentRuptureSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques générales des médicaments"""
        queryset = self.get_queryset()
        
        # Statistiques de base
        total_medicaments = queryset.count()
        medicaments_actifs = queryset.filter(actif=True).count()
        medicaments_rupture = queryset.filter(stock_actuel=0, actif=True).count()
        medicaments_stock_faible = queryset.filter(
            stock_actuel__lte=models.F('stock_minimum'),
            stock_actuel__gt=0,
            actif=True
        ).count()
        
        # Valeur totale du stock
        valeur_stock = queryset.filter(
            prix_unitaire__isnull=False,
            actif=True
        ).aggregate(
            total=Sum(models.F('stock_actuel') * models.F('prix_unitaire'))
        )['total'] or 0
        
        # Nombre de catégories
        categories_count = MedicamentCategorie.objects.filter(
            tenant=request.user.hopital
        ).count() if request.user.hopital else MedicamentCategorie.objects.count()
        
        # Répartition par forme pharmaceutique
        repartition_formes = {}
        formes = queryset.filter(actif=True).values('forme_pharmaceutique').annotate(
            count=Count('medicament_id')
        )
        for forme in formes:
            repartition_formes[forme['forme_pharmaceutique']] = forme['count']
        
        # Top 10 des médicaments les plus chers
        top_chers = queryset.filter(
            prix_unitaire__isnull=False,
            actif=True
        ).order_by('-prix_unitaire')[:10]
        
        top_medicaments_chers = []
        for med in top_chers:
            top_medicaments_chers.append({
                'nom': med.nom,
                'prix_unitaire': float(med.prix_unitaire),
                'stock_actuel': med.stock_actuel,
                'valeur_stock': float(med.prix_unitaire) * med.stock_actuel
            })
        
        # Médicaments nécessitant une attention
        attention_requise = []
        
        # Ruptures de stock
        ruptures = queryset.filter(stock_actuel=0, actif=True)[:5]
        for med in ruptures:
            attention_requise.append({
                'type': 'rupture',
                'medicament': med.nom,
                'message': 'Rupture de stock',
                'priorite': 'haute'
            })
        
        # Stock faible
        stock_faible = queryset.filter(
            stock_actuel__lte=models.F('stock_minimum'),
            stock_actuel__gt=0,
            actif=True
        )[:5]
        for med in stock_faible:
            attention_requise.append({
                'type': 'stock_faible',
                'medicament': med.nom,
                'message': f'Stock faible: {med.stock_actuel}/{med.stock_minimum}',
                'priorite': 'moyenne'
            })
        
        data = {
            'total_medicaments': total_medicaments,
            'medicaments_actifs': medicaments_actifs,
            'medicaments_rupture': medicaments_rupture,
            'medicaments_stock_faible': medicaments_stock_faible,
            'valeur_stock_total': float(valeur_stock),
            'categories_count': categories_count,
            'repartition_formes': repartition_formes,
            'top_medicaments_chers': top_medicaments_chers,
            'attention_requise': attention_requise
        }
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def recherche_avancee(self, request):
        """Recherche avancée de médicaments"""
        serializer = MedicamentRechercheSerializer(data=request.data)
        if serializer.is_valid():
            queryset = self.get_queryset()
            
            # Appliquer les filtres
            if serializer.validated_data.get('nom'):
                queryset = queryset.filter(
                    nom__icontains=serializer.validated_data['nom']
                )
            
            if serializer.validated_data.get('forme_pharmaceutique'):
                queryset = queryset.filter(
                    forme_pharmaceutique=serializer.validated_data['forme_pharmaceutique']
                )
            
            if serializer.validated_data.get('categorie'):
                queryset = queryset.filter(
                    categorie_id=serializer.validated_data['categorie']
                )
            
            if serializer.validated_data.get('code_atc'):
                queryset = queryset.filter(
                    code_atc__icontains=serializer.validated_data['code_atc']
                )
            
            if serializer.validated_data.get('dci'):
                queryset = queryset.filter(
                    dci__icontains=serializer.validated_data['dci']
                )
            
            if serializer.validated_data.get('necessite_ordonnance') is not None:
                queryset = queryset.filter(
                    necessite_ordonnance=serializer.validated_data['necessite_ordonnance']
                )
            
            if serializer.validated_data.get('stock_minimum_atteint'):
                queryset = queryset.filter(
                    stock_actuel__lte=models.F('stock_minimum')
                )
            
            if serializer.validated_data.get('actif') is not None:
                queryset = queryset.filter(
                    actif=serializer.validated_data['actif']
                )
            
            prix_min = serializer.validated_data.get('prix_min')
            prix_max = serializer.validated_data.get('prix_max')
            
            if prix_min:
                queryset = queryset.filter(prix_unitaire__gte=prix_min)
            
            if prix_max:
                queryset = queryset.filter(prix_unitaire__lte=prix_max)
            
            # Paginer les résultats
            page = self.paginate_queryset(queryset)
            if page is not None:
                result_serializer = MedicamentListSerializer(page, many=True)
                return self.get_paginated_response(result_serializer.data)
            
            result_serializer = MedicamentListSerializer(queryset, many=True)
            return Response(result_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def export_stock(self, request):
        """Exporter la liste des médicaments avec leur stock"""
        queryset = self.get_queryset().filter(actif=True).order_by('nom')
        
        # Préparer les données pour l'export
        export_data = []
        for medicament in queryset:
            export_data.append({
                'nom': medicament.nom,
                'forme_pharmaceutique': medicament.get_forme_pharmaceutique_display(),
                'dosage_standard': medicament.dosage_standard or '',
                'categorie': medicament.categorie.nom if medicament.categorie else '',
                'stock_actuel': medicament.stock_actuel,
                'stock_minimum': medicament.stock_minimum,
                'prix_unitaire': float(medicament.prix_unitaire) if medicament.prix_unitaire else 0,
                'valeur_stock': float(medicament.prix_unitaire) * medicament.stock_actuel if medicament.prix_unitaire else 0,
                'necessite_ordonnance': 'Oui' if medicament.necessite_ordonnance else 'Non',
                'statut_stock': 'Rupture' if medicament.stock_actuel == 0 else 'Stock faible' if medicament.besoin_reapprovisionnement else 'Normal'
            })
        
        return Response({
            'data': export_data,
            'total': len(export_data),
            'date_export': timezone.now().isoformat()
        })