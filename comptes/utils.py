# import requests
# from django.conf import settings
# from django.core.mail import send_mail
# from django.urls import reverse

# def send_verification_email(user, token):
#     # Utiliser Brevo ou email standard
#     verification_link = f"https://trimedh-service.onrender.com/api/comptes/verify-email/{token}/"
#     # Ou deep link Android: trimedh://verify?token={token}
    
#     subject = "Vérifiez votre email - TriMedHaiti"
#     message = f"Bonjour {user.nom_complet},\n\nVeuillez cliquer sur le lien pour activer votre compte :\n{verification_link}\n\nCe lien expire dans 24h."
#     html_message = f"<p>Bonjour {user.nom_complet},</p><p>Veuillez <a href='{verification_link}'>cliquer ici</a> pour activer votre compte.</p><p>Ce lien expire dans 24h.</p>"
    
#     # Exemple avec Brevo
#     headers = {'api-key': settings.BREVO_API_KEY, 'Content-Type': 'application/json'}
#     data = {
#         'sender': {'email': 'noreply@trimedhaiti.com', 'name': 'TriMedHaiti'},
#         'to': [{'email': user.email, 'name': user.nom_complet}],
#         'subject': subject,
#         'htmlContent': html_message,
#     }
#     response = requests.post('https://api.brevo.com/v3/smtp/email', json=data, headers=headers)
#     return response.status_code == 201
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

def send_verification_email(user, token):
    backend_url = "https://trimedh-service.onrender.com"
    verification_link = f"{backend_url}/api/comptes/verify-email/{token}/"
    
    # Pour le frontend React (deep link)
    frontend_url = "https://trimedh.vercel.app/"  
    frontend_link = f"{frontend_url}/verification-email?token={token}"
    
    subject = "Vérifiez votre email - TriMedHaiti"
    
    message = f"""
    Bonjour {user.nom_complet},
    
    Veuillez cliquer sur le lien pour activer votre compte :
    {verification_link}
    
    Ce lien expire dans 24h.
    
    Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
    """
    
    html_message = f"""
    <html>
    <body>
        <h2>Bienvenue sur TriMedHaiti</h2>
        <p>Bonjour <strong>{user.nom_complet}</strong>,</p>
        <p>Veuillez cliquer sur le bouton ci-dessous pour activer votre compte :</p>
        <p>
            <a href="{verification_link}" style="background-color:#4CAF50;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">
                Vérifier mon email
            </a>
        </p>
        <p>Ou copiez ce lien dans votre navigateur :</p>
        <p><a href="{verification_link}">{verification_link}</a></p>
        <p>Ce lien expire dans <strong>24 heures</strong>.</p>
        <hr>
        <p><small>Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</small></p>
    </body>
    </html>
    """
    
    # Envoi via Brevo
    headers = {
        'api-key': settings.BREVO_API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'sender': {'email': 'noreply@trimedhaiti.com', 'name': 'TriMedHaiti'},
        'to': [{'email': user.email, 'name': user.nom_complet}],
        'subject': subject,
        'htmlContent': html_message,
        'textContent': message
    }
    
    try:
        response = requests.post('https://api.brevo.com/v3/smtp/email', json=data, headers=headers)
        print(f"Email envoyé à {user.email} - Status: {response.status_code}")
        return response.status_code == 201
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False