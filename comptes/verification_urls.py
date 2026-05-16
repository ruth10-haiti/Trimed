from django.urls import path
from . import admin_validations
from . import verification_api

urlpatterns = [
    # CINU et QR code
    path('verifier-qr-cinu/', admin_validations.verifier_qr_cinu, name='verifier_qr_cinu'),
    path('verifier-ninu-manuel/', admin_validations.verifier_ninu_manuel, name='verifier_ninu_manuel'),
    path('valider-checklist-cinu/', admin_validations.valider_checklist_cinu, name='valider_checklist_cinu'),
    
    # Gestion utilisateurs
    path('utilisateurs-en-attente/', admin_validations.liste_utilisateurs_en_attente, name='utilisateurs_en_attente'),
    path('rejeter-utilisateur/', admin_validations.rejeter_utilisateur, name='rejeter_utilisateur'),
    
    # Analyse documents PDF
    path('analyser-document/', verification_api.analyser_document, name='analyser_document'),
    path('valider-document/', verification_api.valider_document, name='valider_document'),
    path('documents-a-verifier/', verification_api.liste_documents_a_verifier, name='documents_a_verifier'),
    path('document/<int:document_id>/', verification_api.get_document_details, name='document_details'),
]