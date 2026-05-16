from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Document, Utilisateur, DocumentBlacklist, VerificationLog
from .pdf_verification import DocumentAnalyzer, PDFVerificationService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyser_document(request):
    """Étape 1: Analyse automatique du document"""
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=403)
    
    document_id = request.data.get('document_id')
    
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        return Response({'error': 'Document non trouvé'}, status=404)
    
    # Mettre à jour le statut
    document.statut = 'ANALYZING'
    document.save()
    
    # 1. Vérifier doublon
    hash_doc = PDFVerificationService.calculer_hash_pdf(document.fichier.path)
    if hash_doc and DocumentBlacklist.objects.filter(hash_document=hash_doc).exists():
        document.statut = 'REJECTED'
        document.motif_rejet = 'Ce document a déjà été utilisé'
        document.save()
        return Response({
            'success': False,
            'error': 'Ce document a déjà été utilisé',
            'action': 'reject'
        }, status=400)
    
    # 2. Analyser le document
    analyse = DocumentAnalyzer.analyser_document(document)
    
    # 3. Sauvegarder le log
    VerificationLog.objects.create(
        document=document,
        utilisateur=document.utilisateur,
        admin=admin,
        metadata=analyse.get('metadata', {}),
        texte_extrait=analyse.get('texte_extrait', ''),
        informations_extraites=analyse.get('informations', {}),
        qualite_image=analyse.get('qualite', {}),
        detection_falsification=analyse.get('falsification', {}),
        decision=analyse.get('decision_auto', 'PENDING')
    )
    
    # 4. Mettre à jour le document
    document.hash_document = analyse.get('hash_document')
    document.score_confiance = analyse.get('score_confiance', 0)
    document.analyse_resultats = analyse
    
    # Si score très haut, approuver automatiquement
    if analyse.get('score_confiance', 0) >= 85:
        document.statut = 'APPROVED'
        document.valide_par = admin
        document.date_validation = timezone.now()
        document.commentaire_admin = 'Approuvé automatiquement (score confiance élevé)'
        
        # Enregistrer dans blacklist
        if document.hash_document:
            DocumentBlacklist.objects.get_or_create(
                hash_document=document.hash_document,
                defaults={
                    'utilisateur': document.utilisateur,
                    'type_document': document.type_document
                }
            )
        
        # Mettre à jour statut utilisateur
        utilisateur = document.utilisateur
        if document.type_document == 'DIPLOME':
            utilisateur.statut_diplome = 'APPROVED'
        elif document.type_document == 'CARTE_PRO':
            utilisateur.statut_carte_pro = 'APPROVED'
        utilisateur.save()
        
    else:
        document.statut = 'PENDING'
    
    document.save()
    
    return Response({
        'success': True,
        'analyse': {
            'score_confiance': analyse.get('score_confiance'),
            'decision_auto': analyse.get('decision_auto'),
            'message': analyse.get('message'),
            'alertes': analyse.get('alertes', []),
            'informations_extraites': analyse.get('informations', {}),
            'qualite': analyse.get('qualite', {}),
            'falsification': analyse.get('falsification', {})
        },
        'recommandation': analyse.get('decision_auto'),
        'deja_approuve': document.statut == 'APPROVED'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def valider_document(request):
    """Étape 2: Validation manuelle par l'admin"""
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=403)
    
    document_id = request.data.get('document_id')
    decision = request.data.get('decision')  # 'approve' ou 'reject'
    commentaire = request.data.get('commentaire', '')
    checklist = request.data.get('checklist', {})
    
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        return Response({'error': 'Document non trouvé'}, status=404)
    
    # Checklist requise pour approbation
    required_items = ['document_lisible', 'cachet_present', 'signature_present', 'date_valide']
    
    if decision == 'approve':
        # Vérifier checklist
        missing = [item for item in required_items if not checklist.get(item, False)]
        if missing:
            return Response({
                'error': f'Checklist incomplète: {", ".join(missing)}'
            }, status=400)
        
        # Valider le document
        document.statut = 'APPROVED'
        document.valide_par = admin
        document.date_validation = timezone.now()
        document.commentaire_admin = commentaire
        document.save()
        
        # Enregistrer dans blacklist anti-doublon
        if document.hash_document:
            DocumentBlacklist.objects.get_or_create(
                hash_document=document.hash_document,
                defaults={
                    'utilisateur': document.utilisateur,
                    'type_document': document.type_document
                }
            )
        
        # Mettre à jour le log
        VerificationLog.objects.filter(document=document).update(
            decision='MANUAL_APPROVED',
            commentaire_admin=commentaire
        )
        
        # Mettre à jour le statut de l'utilisateur
        utilisateur = document.utilisateur
        if document.type_document == 'DIPLOME':
            utilisateur.statut_diplome = 'APPROVED'
        elif document.type_document == 'CARTE_PRO':
            utilisateur.statut_carte_pro = 'APPROVED'
        elif document.type_document == 'CINU':
            utilisateur.statut_cinu = 'APPROVED'
        
        utilisateur.save()
        
        # Vérifier si tous les documents sont validés
        tous_valides = True
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
            send_validation_email(utilisateur)
        
        return Response({
            'success': True,
            'message': 'Document validé avec succès',
            'compte_active': tous_valides
        })
    
    elif decision == 'reject':
        document.statut = 'REJECTED'
        document.motif_rejet = commentaire
        document.save()
        
        VerificationLog.objects.filter(document=document).update(
            decision='REJECTED',
            commentaire_admin=commentaire
        )
        
        return Response({
            'success': True,
            'message': 'Document rejeté',
            'motif': commentaire
        })
    
    return Response({'error': 'Décision invalide'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_documents_a_verifier(request):
    """Liste des documents en attente de vérification"""
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=403)
    
    documents = Document.objects.filter(statut='PENDING').select_related('utilisateur')
    
    resultats = []
    for doc in documents:
        resultats.append({
            'id': doc.id,
            'type_document': doc.type_document,
            'type_display': doc.get_type_document_display(),
            'utilisateur': {
                'id': doc.utilisateur.utilisateur_id,
                'nom_complet': doc.utilisateur.nom_complet,
                'email': doc.utilisateur.email,
                'role': doc.utilisateur.role,
                'statut_cinu': doc.utilisateur.statut_cinu,
                'statut_diplome': doc.utilisateur.statut_diplome,
                'statut_carte_pro': doc.utilisateur.statut_carte_pro
            },
            'nom_fichier': doc.nom_fichier_original,
            'taille': doc.taille_fichier,
            'date_upload': doc.date_upload.isoformat(),
            'file_url': doc.fichier.url,
            'score_confiance': doc.score_confiance
        })
    
    return Response({
        'documents': resultats,
        'total': len(resultats)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_details(request, document_id):
    """Détails d'un document spécifique"""
    admin = request.user
    
    if admin.role not in ['admin-systeme', 'proprietaire-hopital']:
        return Response({'error': 'Accès non autorisé'}, status=403)
    
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        return Response({'error': 'Document non trouvé'}, status=404)
    
    return Response({
        'id': document.id,
        'type_document': document.type_document,
        'type_display': document.get_type_document_display(),
        'utilisateur': {
            'id': document.utilisateur.utilisateur_id,
            'nom_complet': document.utilisateur.nom_complet,
            'email': document.utilisateur.email,
            'role': document.utilisateur.role
        },
        'nom_fichier': document.nom_fichier_original,
        'taille': document.taille_fichier,
        'date_upload': document.date_upload.isoformat(),
        'file_url': document.fichier.url,
        'statut': document.statut,
        'score_confiance': document.score_confiance,
        'analyse_resultats': document.analyse_resultats,
        'commentaire_admin': document.commentaire_admin,
        'motif_rejet': document.motif_rejet
    })


def send_validation_email(utilisateur):
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
        print(f"Erreur envoi email: {e}")