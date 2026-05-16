import hashlib
import re
import io
from datetime import datetime
from PIL import Image
import fitz  # PyMuPDF
import PyPDF2

class PDFVerificationService:
    """Service complet de vérification des documents PDF"""
    
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
        """Extrait les métadonnées du PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata if pdf_reader.metadata else {}
                
                return {
                    'auteur': metadata.get('/Author', 'Inconnu'),
                    'createur': metadata.get('/Creator', 'Inconnu'),
                    'producteur': metadata.get('/Producer', 'Inconnu'),
                    'date_creation': metadata.get('/CreationDate', 'Inconnu'),
                    'nb_pages': len(pdf_reader.pages),
                    'logiciel_suspect': PDFVerificationService._detecter_logiciel_suspect(metadata)
                }
        except Exception as e:
            return {'erreur': str(e), 'logiciel_suspect': True, 'nb_pages': 1}
    
    @staticmethod
    def _detecter_logiciel_suspect(metadata):
        """Détecte les logiciels de modification suspects"""
        logiciels_suspects = [
            'Adobe Photoshop', 'GIMP', 'Pixelmator', 
            'Microsoft Word', 'LibreOffice', 'Canva',
            'Photoshop', 'Illustrator', 'InDesign',
            'Paint', 'PDF Editor', 'PDFescape', 'PaintTool'
        ]
        
        if metadata:
            createur = str(metadata.get('/Creator', ''))
            producteur = str(metadata.get('/Producer', ''))
            
            for logiciel in logiciels_suspects:
                if logiciel.lower() in createur.lower() or logiciel.lower() in producteur.lower():
                    return True
        return False
    
    @staticmethod
    def extraire_texte_pdf(pdf_path):
        """Extrait le texte complet du PDF"""
        try:
            doc = fitz.open(pdf_path)
            texte_complet = ""
            
            for page in doc:
                texte_complet += page.get_text()
            
            doc.close()
            return ' '.join(texte_complet.split())
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
        """Vérifie la qualité du scan"""
        try:
            doc = fitz.open(pdf_path)
            premiere_page = doc[0]
            
            # Convertir en image pour analyse
            pix = premiere_page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            largeur, hauteur = img.size
            
            doc.close()
            
            return {
                'resolution': f"{largeur}x{hauteur}",
                'est_lisible': largeur >= 1000 and hauteur >= 700,
                'nb_pages': len(doc),
                'taille_pixels': largeur * hauteur
            }
        except Exception as e:
            return {'erreur': str(e), 'est_lisible': False, 'nb_pages': 1}
    
    @staticmethod
    def detection_falsification(pdf_path):
        """Détection de falsifications basiques"""
        try:
            doc = fitz.open(pdf_path)
            elements_suspects = []
            
            for page_num, page in enumerate(doc):
                # Trop d'images = possible Photoshop
                images = page.get_images()
                if len(images) > 3:
                    elements_suspects.append(f"Page {page_num+1}: {len(images)} images (modification suspecte)")
                
                # Annotations = modifications
                annotations = list(page.annots())
                if annotations:
                    elements_suspects.append(f"Page {page_num+1}: Annotations/modifications détectées")
                
                # Champs formulaire = document éditable
                widgets = list(page.widgets())
                if widgets:
                    elements_suspects.append(f"Page {page_num+1}: Champs modifiables détectés")
            
            doc.close()
            
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
        
        # 5. Qualité image
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
        
        if metadata.get('nb_pages', 0) > 3:
            score_confiance -= 10
            alertes.append("Document anormalement long (plus de 3 pages)")
        
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
            'texte_extrait': texte[:2000]
        }