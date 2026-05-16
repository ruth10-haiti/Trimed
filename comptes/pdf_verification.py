import hashlib
import re
import io
from datetime import datetime
from PIL import Image
import PyPDF2
import pdfplumber
from django.core.files.storage import default_storage

class PDFVerificationService:
    """Service complet de vérification des documents PDF (sans PyMuPDF)"""
    
    # Universités reconnues en Haïti
    UNIVERSITES_RECONNUES = [
        "UNIVERSITÉ D'ÉTAT D'HAÏTI", "UEH",
        "UNIVERSITÉ QUISQUEYA", "UNIQ",
        "UNIVERSITÉ NOTRE-DAME D'HAÏTI", "UNDH",
        "UNIVERSITÉ CARAÏBE", "UNICAR",
        "UNIVERSITÉ AMÉRICAINE", "UAM",
        "UNIVERSITÉ FONDATION DR ARIEL HENRY", "UFDAH",
        "UNIVERSITÉ CHRÉTIENNE DU NORD D'HAÏTI", "UCNH",
        "UNIVERSITÉ JEAN PRICE MARS", "UJPM",
        "UNIVERSITÉ ROYALE D'HAÏTI", "URH",
        "FACULTÉ DE MÉDECINE ET DE PHARMACIE", "FMP",
        "FACULTÉ DES SCIENCES INFIRMIÈRES"
    ]
    
    @staticmethod
    def calculer_hash_pdf(pdf_path):
        """Calcule le hash SHA256 du document"""
        try:
            with open(pdf_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return None
    
    @staticmethod
    def extraire_metadonnees(pdf_path):
        """Extrait les métadonnées du PDF avec PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata if pdf_reader.metadata else {}
                
                return {
                    'auteur': metadata.get('/Author', 'Inconnu') if metadata else 'Inconnu',
                    'createur': metadata.get('/Creator', 'Inconnu') if metadata else 'Inconnu',
                    'producteur': metadata.get('/Producer', 'Inconnu') if metadata else 'Inconnu',
                    'date_creation': metadata.get('/CreationDate', 'Inconnu') if metadata else 'Inconnu',
                    'nb_pages': len(pdf_reader.pages),
                    'logiciel_suspect': PDFVerificationService._detecter_logiciel_suspect(metadata)
                }
        except Exception as e:
            return {'erreur': str(e), 'logiciel_suspect': True, 'nb_pages': 1}
    
    @staticmethod
    def _detecter_logiciel_suspect(metadata):
        """Détecte les logiciels de modification suspects"""
        if not metadata:
            return True
        
        logiciels_suspects = [
            'Adobe Photoshop', 'GIMP', 'Pixelmator', 
            'Microsoft Word', 'LibreOffice', 'Canva',
            'Photoshop', 'Illustrator', 'InDesign',
            'Paint', 'PDF Editor', 'PDFescape', 'PaintTool'
        ]
        
        createur = str(metadata.get('/Creator', ''))
        producteur = str(metadata.get('/Producer', ''))
        
        for logiciel in logiciels_suspects:
            if logiciel.lower() in createur.lower() or logiciel.lower() in producteur.lower():
                return True
        return False
    
    @staticmethod
    def extraire_texte_pdf(pdf_path):
        """Extrait le texte du PDF avec pdfplumber (meilleur OCR intégré)"""
        try:
            texte_complet = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        texte_complet += page_text + " "
                    
                    # Tentative d'extraction des tables si présentes
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            texte_complet += " ".join([str(cell) for cell in row if cell]) + " "
            
            return ' '.join(texte_complet.split()) if texte_complet else ""
        except Exception as e:
            return f"Erreur extraction: {str(e)}"
    
    @staticmethod
    def extraire_informations_diplome(texte):
        """Extrait les informations clés du diplôme"""
        informations = {
            'numero_diplome': None,
            'universite': None,
            'diplome_type': None,
            'date_obtention': None,
            'mention': None,
            'nom_etudiant': None,
            'est_reconnu': False
        }
        
        if not texte:
            return informations
        
        # Patterns regex
        patterns = {
            'numero_diplome': r'(?:N[°°]\s*|Numéro\s*|N°\s*|No\s*)(\d{5,15})',
            'universite': r'(UNIVERSITÉ|UNIVERSITE|FACULTÉ|ECOLE)[\s\S]{0,100}(?:D\'|D’|DE\s+)?[A-Z\s]{3,50}',
            'diplome_type': r'(DOCTEUR EN MÉDECINE|DOCTORAT EN MÉDECINE|DIPLÔME D\'ÉTAT|LICENCE|MASTER|BACCALAURÉAT|DOCTORAT|SPÉCIALISTE|DIPLOME)',
            'date_obtention': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'mention': r'(MENTION|MENTION\s+)(TRÈS BIEN|BIEN|ASSEZ BIEN|PASSABLE)',
            'nom_etudiant': r'(?:M(?:onsieur|adame|lle)?|Étudiant|Étudiante)\s+([A-Z][A-Z\s]{2,30})'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                if key == 'numero_diplome':
                    informations[key] = match.group(1)
                elif key == 'mention':
                    informations[key] = match.group(2) if match.group(2) else match.group(0)
                else:
                    informations[key] = match.group(0).strip()
        
        # Vérifier si l'université est reconnue
        if informations['universite']:
            universite_upper = informations['universite'].upper()
            for uni in PDFVerificationService.UNIVERSITES_RECONNUES:
                if uni in universite_upper:
                    informations['est_reconnu'] = True
                    break
        
        return informations
    
    @staticmethod
    def verifier_qualite_image(pdf_path):
        """Vérifie la qualité du document (basé sur la première page)"""
        try:
            # Avec pdfplumber, on peut avoir un aperçu
            with pdfplumber.open(pdf_path) as pdf:
                nb_pages = len(pdf.pages)
                premiere_page = pdf.pages[0]
                
                # Estimation de la qualité basée sur le texte extrait
                texte_page = premiere_page.extract_text() or ""
                longueur_texte = len(texte_page)
                
                # Qualité estimée
                est_lisible = longueur_texte > 100  # Si plus de 100 caractères, probablement lisible
            
            return {
                'resolution': 'Estimation basée sur le texte',
                'est_lisible': est_lisible,
                'nb_pages': nb_pages,
                'taille_pixels': 0
            }
        except Exception as e:
            return {'erreur': str(e), 'est_lisible': False, 'nb_pages': 1}
    
    @staticmethod
    def detection_falsification(pdf_path):
        """Détection de falsifications basiques avec PyPDF2"""
        try:
            elements_suspects = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Vérifier les annotations
                for page_num, page in enumerate(pdf_reader.pages):
                    if '/Annots' in page:
                        elements_suspects.append(f"Page {page_num+1}: Annotations/modifications détectées")
                    
                    # Vérifier les champs de formulaire
                    if '/AcroForm' in pdf_reader.trailer.get('/Root', {}):
                        elements_suspects.append(f"Page {page_num+1}: Champs de formulaire détectés")
            
            # Vérifier la cohérence du nombre de pages
            if len(pdf_reader.pages) > 5:
                elements_suspects.append(f"Document anormalement long ({len(pdf_reader.pages)} pages)")
            
            return {
                'est_falsifie': len(elements_suspects) > 0,
                'elements_suspects': elements_suspects,
                'niveau_risque': 'HAUT' if len(elements_suspects) > 2 else 'MOYEN' if elements_suspects else 'FAIBLE'
            }
        except Exception as e:
            return {'est_falsifie': True, 'erreur': str(e), 'niveau_risque': 'INCONNU'}


class DocumentAnalyzer:
    """Analyseur complet de documents"""
    
    @staticmethod
    def analyser_document(document):
        """Analyse complète d'un document"""
        pdf_path = document.fichier.path
        
        # 1. Hash anti-doublon
        hash_doc = PDFVerificationService.calculer_hash_pdf(pdf_path)
        
        # 2. Métadonnées
        metadata = PDFVerificationService.extraire_metadonnees(pdf_path)
        
        # 3. Texte extrait
        texte = PDFVerificationService.extraire_texte_pdf(pdf_path)
        
        # 4. Informations spécifiques
        infos = PDFVerificationService.extraire_informations_diplome(texte)
        
        # 5. Qualité
        qualite = PDFVerificationService.verifier_qualite_image(pdf_path)
        
        # 6. Détection falsification
        falsification = PDFVerificationService.detection_falsification(pdf_path)
        
        # 7. Calcul du score de confiance
        score_confiance = 100
        alertes = []
        
        # Critères de déduction
        if metadata.get('logiciel_suspect', False):
            score_confiance -= 30
            alertes.append("Document créé/modifié avec logiciel suspect (Photoshop, Word, etc.)")
        
        if not infos.get('est_reconnu', False):
            score_confiance -= 25
            alertes.append("Université non reconnue ou non vérifiée")
        
        if not qualite.get('est_lisible', False):
            score_confiance -= 30
            alertes.append("Qualité d'image insuffisante (document flou ou trop petit)")
        
        if falsification.get('est_falsifie', False):
            score_confiance -= 40
            alertes.extend(falsification.get('elements_suspects', []))
        
        if not infos.get('numero_diplome'):
            score_confiance -= 20
            alertes.append("Numéro de diplôme non trouvé")
        
        if not infos.get('date_obtention'):
            score_confiance -= 10
            alertes.append("Date d'obtention non trouvée")
        
        if metadata.get('nb_pages', 0) > 5:
            score_confiance -= 10
            alertes.append("Document anormalement long (plus de 5 pages)")
        
        # Score minimum 0
        score_confiance = max(0, score_confiance)
        
        # Décision automatique
        if score_confiance >= 80:
            decision_auto = 'AUTO_APPROVED'
            message = "Document semble authentique (confiance élevée)"
        elif score_confiance >= 50:
            decision_auto = 'MANUAL_REVIEW'
            message = "Document nécessite vérification manuelle approfondie"
        else:
            decision_auto = 'REJECTED'
            message = "Document suspect - recommandation de rejet"
        
        return {
            'hash_document': hash_doc,
            'score_confiance': score_confiance,
            'decision_auto': decision_auto,
            'message': message,
            'alertes': alertes,
            'informations': infos,
            'qualite': qualite,
            'metadata': metadata,
            'falsification': falsification,
            'texte_extrait': texte[:2000] if texte else ""
        }