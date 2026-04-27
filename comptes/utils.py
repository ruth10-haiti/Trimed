import requests
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

def send_verification_email(user, token):
    # Utiliser Brevo ou email standard
    verification_link = f"https://trimedh-service.onrender.com/api/comptes/verify-email/{token}/"
    # Ou deep link Android: trimedh://verify?token={token}
    
    subject = "Vérifiez votre email - TriMedHaiti"
    message = f"Bonjour {user.nom_complet},\n\nVeuillez cliquer sur le lien pour activer votre compte :\n{verification_link}\n\nCe lien expire dans 24h."
    html_message = f"<p>Bonjour {user.nom_complet},</p><p>Veuillez <a href='{verification_link}'>cliquer ici</a> pour activer votre compte.</p><p>Ce lien expire dans 24h.</p>"
    
    # Exemple avec Brevo
    headers = {'api-key': settings.BREVO_API_KEY, 'Content-Type': 'application/json'}
    data = {
        'sender': {'email': 'noreply@trimedhaiti.com', 'name': 'TriMedHaiti'},
        'to': [{'email': user.email, 'name': user.nom_complet}],
        'subject': subject,
        'htmlContent': html_message,
    }
    response = requests.post('https://api.brevo.com/v3/smtp/email', json=data, headers=headers)
    return response.status_code == 201