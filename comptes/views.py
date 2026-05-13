from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from .utils import send_verification_email
import threading
import json
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from .serializers import InscriptionSerializer   
from .models import Utilisateur, EmailVerificationToken
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from .serializers import (
    UtilisateurSerializer, InscriptionSerializer,
    LoginSerializer, ChangePasswordSerializer, UpdateProfileSerializer
)
from .permissions import (
    EstAdminSysteme, EstProprietaireHopital, EstMedecin,
    EstPersonnel, EstPatient, PeutModifierUtilisateur
)


class UtilisateurViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs
    """
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'hopital', 'is_active']
    search_fields = ['email', 'nom_complet']
    ordering_fields = ['nom_complet', 'cree_le', 'derniere_connexion']

    def get_permissions(self):
        """Permissions personnalisées selon l'action"""
        if self.action == 'create':
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, PeutModifierUtilisateur]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated, EstAdminSysteme | EstProprietaireHopital | EstMedecin]
        return [permission() for permission in permission_classes]
    

    def get_queryset(self):
        """Filtrer les utilisateurs selon les permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'admin-systeme':
            return queryset

        if user.role == 'proprietaire-hopital' and user.hopital:
            return queryset.filter(hopital=user.hopital)

        if user.role == 'medecin' and user.hopital:
            return queryset.filter(hopital=user.hopital).exclude(role='patient')

        if user.role in ['personnel', 'secretaire', 'infirmier'] and user.hopital:
            return queryset.filter(hopital=user.hopital).exclude(role='patient')

        if user.role == 'patient':
            return queryset.filter(pk=user.pk)

        return Utilisateur.objects.none()

    def perform_create(self, serializer):
        """Surcharge pour enregistrer qui a créé l'utilisateur"""
        serializer.save(modifie_par=self.request.user)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Récupérer le profil de l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Mettre à jour le profil de l'utilisateur connecté"""
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Changer le mot de passe d'un utilisateur"""
        utilisateur = self.get_object()

        if utilisateur != request.user and not (
            request.user.role in ['admin-systeme', 'proprietaire-hopital']
        ):
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier ce mot de passe'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not utilisateur.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Mot de passe incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            utilisateur.set_password(serializer.validated_data['new_password'])
            utilisateur.save()

            return Response({'message': 'Mot de passe mis à jour avec succès'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activer/désactiver un utilisateur"""
        utilisateur = self.get_object()

        if request.user.role not in ['admin-systeme', 'proprietaire-hopital']:
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier cet utilisateur'},
                status=status.HTTP_403_FORBIDDEN
            )

        utilisateur.is_active = not utilisateur.is_active
        utilisateur.save()

        status_msg = 'activé' if utilisateur.is_active else 'désactivé'
        return Response({
            'message': f'Utilisateur {status_msg} avec succès',
            'is_active': utilisateur.is_active
        })


class LoginView(APIView):
    """Vue pour l'authentification"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            utilisateur = serializer.validated_data['utilisateur']

            # Générer les tokens JWT
            refresh = RefreshToken.for_user(utilisateur)

            # Sérialiser les données utilisateur
            user_serializer = UtilisateurSerializer(utilisateur)
            user_data = user_serializer.data

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data,
                'tenant': user_data.get('hopital_detail')
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Vue pour la déconnexion"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response(
                {'message': 'Déconnexion réussie'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class InscriptionView(APIView):
    """Vue pour l'inscription des hôpitaux avec vérification email"""
    
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        # 1. Validation des données utilisateur
        serializer = InscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2. Création de l'utilisateur (is_active=False par défaut)
        utilisateur = serializer.save()

        # 3. Forcer le rôle (propriétaire d'hôpital) et désactiver le compte
        utilisateur.role = 'proprietaire-hopital'
        utilisateur.is_active = False
        utilisateur.save(update_fields=['role', 'is_active'])

        # 4. Récupération des données de l'hôpital (tenant) – optionnel
        hopital_data_raw = request.data.get('hopital_data')
        hopital_data = None
        if hopital_data_raw:
            if isinstance(hopital_data_raw, str):
                try:
                    hopital_data = json.loads(hopital_data_raw)
                except json.JSONDecodeError:
                    hopital_data = None
            elif isinstance(hopital_data_raw, dict):
                hopital_data = hopital_data_raw

        tenant = None
        if hopital_data:
            from gestion_tenants.models import Tenant
            nombre_lits = int(hopital_data.get('nombre_de_lits', 1))
            if nombre_lits < 1:
                nombre_lits = 1

            tenant = Tenant.objects.create(
                nom=hopital_data.get('nom', ''),
                adresse=hopital_data.get('adresse', ''),
                telephone=hopital_data.get('telephone', ''),
                email_professionnel=hopital_data.get('email_professionnel', ''),
                directeur=hopital_data.get('directeur', ''),
                nombre_de_lits=nombre_lits,
                numero_enregistrement=hopital_data.get('numero_enregistrement', ''),
                statut='inactif',
                type_abonnement=hopital_data.get('type_abonnement', 'basic'),
                statut_verification_document='en_attente',
                nom_schema_base_de_donnees=hopital_data.get('nom_schema_base_de_donnees', ''),
                proprietaire_utilisateur=utilisateur,
                cree_par_utilisateur=utilisateur,
            )
            # Associer le tenant à l'utilisateur
            utilisateur.hopital = tenant
            utilisateur.save(update_fields=['hopital'])

        # 5. Créer un token de vérification email (expiration 24h)
        token_obj = EmailVerificationToken.objects.create(
            utilisateur=utilisateur,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # 6. Envoi de l'email en arrière‑plan (ne bloque pas la réponse)
        threading.Thread(
            target=send_verification_email,
            args=(utilisateur, str(token_obj.token)),
            daemon=True
        ).start()

        # 7. Réponse finale (pas de token JWT car compte inactif)
        return Response({
            'success': True,
            'message': 'Inscription réussie. Vérifiez votre email pour activer votre compte.',
            'user': {
                'id': utilisateur.pk,
                'email': utilisateur.email,
                'nom_complet': utilisateur.nom_complet,
                'role': utilisateur.role,
                'is_active': utilisateur.is_active,
                'hopital_id': tenant.pk if tenant else None,
                'hopital_nom': tenant.nom if tenant else None,
            },
            'tenant': {
                'id': tenant.pk,
                'nom': tenant.nom,
                'statut': tenant.statut,
            } if tenant else None
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    """
    Vérification d'email - Redirige vers le frontend Vercel
    """
    print(f"🔍 Vérification email avec token: {token}")
    
    frontend_url = "https://trimedh.vercel.app"
    
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        
        if token_obj.is_valid():
            print(f" Token valide pour: {token_obj.utilisateur.email}")
            
            # Activer le compte
            token_obj.verified_at = timezone.now()
            token_obj.utilisateur.is_active = True
            token_obj.utilisateur.save()
            token_obj.save()
            
            # Rediriger vers la page de connexion du frontend avec succès
            redirect_url = f"{frontend_url}/connexion?verification=success&email={token_obj.utilisateur.email}"
            return redirect(redirect_url)
            
        else:
            print("Token expiré ou invalide")
            # Rediriger vers connexion avec erreur
            redirect_url = f"{frontend_url}/connexion?verification=error&message=token_expired"
            return redirect(redirect_url)
            
    except EmailVerificationToken.DoesNotExist:
        print("Token non trouvé")
        redirect_url = f"{frontend_url}/connexion?verification=error&message=invalid_token"
        return redirect(redirect_url)