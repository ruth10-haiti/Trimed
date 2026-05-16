from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from .models import (
    Utilisateur, Document, DocumentBlacklist, 
    CINUBlacklist, VerificationLog
)
from .pdf_verification import PDFVerificationService, DocumentAnalyzer
import hashlib
import json
import re
from datetime import datetime


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verifier_qr_cinu(request):
    """
    Vérification d'une CINU via QR code scanné
    """
    admin = request.user
    
    # Vérifier que l'utilisateur est admin
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({
            'error': 'Accès non autorisé. Droits administrateur requis.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    qr_string = request.data.get('qr_string')
    user_id = request.data.get('user_id')
    
    if not qr_string:
        return Response({
            'error': 'QR code requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 1. Décoder le QR code
    try:
        qr_data = json.loads(qr_string)
    except json.JSONDecodeError:
        return Response({
            'error': 'QR code invalide (format JSON non reconnu)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. Vérifier les champs obligatoires
    required_fields = ['ninu', 'nom', 'prenom']
    missing_fields = [f for f in required_fields if f not in qr_data]
    if missing_fields:
        return Response({
            'error': f'Champs manquants dans le QR code: {", ".join(missing_fields)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 3. Valider le format NINU (14 chiffres pour nouvelle version)
    ninu = qr_data['ninu']
    if not re.match(r'^\d{14}$', ninu):
        return Response({
            'error': 'Le NINU doit contenir exactement 14 chiffres (CINU nouvelle version)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 4. Vérifier anti-doublon
    ninu_hash = hashlib.sha256(ninu.encode()).hexdigest()
    if CINUBlacklist.objects.filter(ninu_hash=ninu_hash).exists():
        existing = CINUBlacklist.objects.get(ninu_hash=ninu_hash)
        return Response({
            'error': 'Cette CINU a déjà été utilisée pour un autre compte',
            'utilisateur_existant': existing.utilisateur.nom_complet,
            'date_utilisation': existing.date_utilisation.strftime('%d/%m/%Y')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 5. Récupérer l'utilisateur
    try:
        utilisateur = Utilisateur.objects.get(utilisateur_id=user_id)
    except Utilisateur.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 6. Comparer les données du QR avec la saisie utilisateur
    errors = []
    nom_qr = qr_data['nom'].upper().strip()
    nom_utilisateur = utilisateur.nom_complet.upper().split()[0] if utilisateur.nom_complet else ""
    
    if nom_qr != nom_utilisateur:
        errors.append(f"Nom: '{qr_data['nom']}' vs '{nom_utilisateur}'")
    
    prenom_qr = qr_data['prenom'].upper().strip()
    prenom_utilisateur = ' '.join(utilisateur.nom_complet.upper().split()[1:]) if len(utilisateur.nom_complet.split()) > 1 else ""
    
    if prenom_qr != prenom_utilisateur:
        errors.append(f"Prénom: '{qr_data['prenom']}' vs '{prenom_utilisateur}'")
    
    if errors:
        return Response({
            'error': 'Les données de la CINU ne correspondent pas aux informations saisies',
            'details': errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 7. Sauvegarder les informations
    utilisateur.ninu = ninu
    utilisateur.version_cinu = 'V2'
    utilisateur.qr_code_data = qr_data
    utilisateur.statut_cinu = 'SCAN_VALIDE'
    utilisateur.save()
    
    # 8. Enregistrer dans la blacklist
    CINUBlacklist.objects.create(
        ninu_hash=ninu_hash,
        utilisateur=utilisateur
    )
    
    # 9. Log l'action
    VerificationLog.objects.create(
        document=None,
        utilisateur=utilisateur,
        admin=admin,
        decision='SCAN_QR',
        commentaire_admin=f"QR code scanné - NINU: {ninu}",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return Response({
        'success': True,
        'message': 'CINU vérifiée avec succès',
        'data': {
            'ninu': ninu,
            'nom': qr_data['nom'],
            'prenom': qr_data['prenom'],
            'version': 'V2'
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verifier_ninu_manuel(request):
    """
    Vérification manuelle du NINU (pour ordinateur sans caméra)
    """
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    ninu = request.data.get('ninu')
    user_id = request.data.get('user_id')
    
    if not ninu:
        return Response({'error': 'NINU requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 1. Vérifier format (14 chiffres)
    if not re.match(r'^\d{14}$', ninu):
        return Response({
            'error': 'Le NINU doit contenir exactement 14 chiffres'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. Vérifier anti-doublon
    ninu_hash = hashlib.sha256(ninu.encode()).hexdigest()
    if CINUBlacklist.objects.filter(ninu_hash=ninu_hash).exists():
        return Response({
            'error': 'Cette CINU a déjà été utilisée pour un autre compte'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 3. Récupérer utilisateur
    try:
        utilisateur = Utilisateur.objects.get(utilisateur_id=user_id)
    except Utilisateur.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    
    # 4. Sauvegarder
    utilisateur.ninu = ninu
    utilisateur.version_cinu = 'V2'
    utilisateur.statut_cinu = 'NINU_SAISI'
    utilisateur.save()
    
    # 5. Blacklist
    CINUBlacklist.objects.create(
        ninu_hash=ninu_hash,
        utilisateur=utilisateur
    )
    
    # Extraire département depuis les 2 premiers chiffres
    dept_code = ninu[:2]
    departements = {
        '01': 'Ouest', '02': 'Nord', '03': 'Nord-Est',
        '04': 'Artibonite', '05': 'Sud', '06': 'Sud-Est',
        '07': 'Grande-Anse', '08': 'Nord-Ouest', '09': 'Centre',
        '10': 'Nippes'
    }
    
    return Response({
        'success': True,
        'message': 'NINU vérifié avec succès',
        'data': {
            'ninu': ninu,
            'departement_emission': departements.get(dept_code, 'Inconnu')
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def valider_checklist_cinu(request):
    """
    Validation finale de la CINU avec checklist visuelle
    """
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    checklist = request.data.get('checklist', {})
    commentaire = request.data.get('commentaire', '')
    
    # Éléments requis
    required_items = ['format_carte', 'puce_electronique', 'photo', 'signature', 'date_expiration']
    missing = [item for item in required_items if not checklist.get(item, False)]
    
    if missing:
        items_labels = {
            'format_carte': 'Carte en plastique rigide',
            'puce_electronique': 'Puce électronique visible',
            'photo': 'Photo d\'identité nette',
            'signature': 'Signature présente',
            'date_expiration': 'Date d\'expiration valide'
        }
        missing_labels = [items_labels.get(m, m) for m in missing]
        return Response({
            'error': f'Checklist incomplète: {", ".join(missing_labels)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        utilisateur = Utilisateur.objects.get(utilisateur_id=user_id)
    except Utilisateur.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    
    # Valider la CINU
    utilisateur.statut_cinu = 'APPROVED'
    utilisateur.save()
    
    # Log
    VerificationLog.objects.create(
        document=None,
        utilisateur=utilisateur,
        admin=admin,
        decision='MANUAL_APPROVED',
        commentaire_admin=f"Checklist validée: {commentaire}" if commentaire else "Checklist complète",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Vérifier si tous les documents sont validés selon le rôle
    tous_valides = False
    if utilisateur.role == 'medecin':
        tous_valides = (utilisateur.statut_cinu == 'APPROVED' and 
                       utilisateur.statut_diplome == 'APPROVED')
    elif utilisateur.role == 'infirmier':
        tous_valides = (utilisateur.statut_cinu == 'APPROVED' and 
                       utilisateur.statut_carte_pro == 'APPROVED')
    elif utilisateur.role == 'patient':
        tous_valides = utilisateur.statut_cinu == 'APPROVED'
    
    if tous_valides and not utilisateur.est_verifie:
        utilisateur.est_verifie = True
        utilisateur.date_validation = timezone.now()
        utilisateur.valide_par = admin
        utilisateur.save()
        
        # Envoyer email de validation
        envoyer_email_validation(utilisateur)
    
    return Response({
        'success': True,
        'message': 'CINU validée avec succès',
        'compte_active': tous_valides
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_utilisateurs_en_attente(request):
    """
    Liste des utilisateurs avec documents en attente de validation
    """
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les utilisateurs non vérifiés
    utilisateurs = Utilisateur.objects.filter(est_verifie=False).exclude(role='admin-systeme')
    
    resultats = []
    for user in utilisateurs:
        resultats.append({
            'id': user.utilisateur_id,
            'nom_complet': user.nom_complet,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'statut_cinu': user.statut_cinu,
            'statut_diplome': user.statut_diplome,
            'statut_carte_pro': user.statut_carte_pro,
            'date_inscription': user.cree_le.strftime('%d/%m/%Y %H:%M'),
            'documents': [
                {
                    'id': doc.id,
                    'type': doc.type_document,
                    'type_display': doc.get_type_document_display(),
                    'statut': doc.statut,
                    'date_upload': doc.date_upload.strftime('%d/%m/%Y %H:%M')
                }
                for doc in user.documents.all()
            ]
        })
    
    return Response({
        'utilisateurs': resultats,
        'total': len(resultats)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rejeter_utilisateur(request):
    """
    Rejeter un utilisateur avec motif
    """
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    motif = request.data.get('motif', '')
    
    if not motif:
        return Response({'error': 'Motif de rejet requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        utilisateur = Utilisateur.objects.get(utilisateur_id=user_id)
    except Utilisateur.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    
    # Désactiver le compte
    utilisateur.is_active = False
    utilisateur.est_verifie = False
    utilisateur.save()
    
    # Rejeter tous les documents
    Document.objects.filter(utilisateur=utilisateur, statut='PENDING').update(
        statut='REJECTED',
        motif_rejet=motif
    )
    
    # Log
    VerificationLog.objects.create(
        document=None,
        utilisateur=utilisateur,
        admin=admin,
        decision='REJECTED',
        commentaire_admin=motif,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Envoyer email de rejet
    envoyer_email_rejet(utilisateur, motif)
    
    return Response({
        'success': True,
        'message': f'Utilisateur {utilisateur.nom_complet} rejeté',
        'motif': motif
    })


def envoyer_email_validation(utilisateur):
    """Envoie l'email de validation du compte"""
    subject = "Votre compte TrimedH est validé !"
    message = f"""
    Bonjour {utilisateur.nom_complet},
    
    Félicitations ! Votre compte a été validé par l'administrateur.
    
    Vous pouvez maintenant vous connecter à l'application TrimedH.
    
    Email: {utilisateur.email}
    
    Lien de connexion: https://trimedh-service.onrender.com/login
    
    Cordialement,
    L'équipe TrimedH
    """
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [utilisateur.email])
    except Exception as e:
        print(f"Erreur envoi email validation: {e}")


def envoyer_email_rejet(utilisateur, motif):
    """Envoie l'email de rejet"""
    subject = "Votre compte TrimedH - Dossier rejeté"
    message = f"""
    Bonjour {utilisateur.nom_complet},
    
    Nous vous informons que votre dossier d'inscription n'a pas été approuvé.
    
    Motif du rejet: {motif}
    
    Vous pouvez contacter l'administrateur pour plus d'informations ou soumettre un nouveau dossier.
    
    Cordialement,
    L'équipe TrimedH
    """
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [utilisateur.email])
    except Exception as e:
        print(f"Erreur envoi email rejet: {e}")