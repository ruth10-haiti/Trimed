import requests
from django.conf import settings

def send_verification_email(user, token):
    """
    Envoie un email de vérification à l'utilisateur
    """
    # Utiliser BACKEND_URL depuis settings
    backend_url = getattr(settings, 'BACKEND_URL', 'https://trimedh-service.onrender.com')
    verification_link = f"{backend_url}/api/comptes/verify-email/{token}/"
    
    subject = "Vérifiez votre email - TriMedHaiti"
    
    message = f"""
    Bonjour {user.nom_complet},
    
    Veuillez cliquer sur le lien pour activer votre compte :
    {verification_link}
    
    Après vérification, vous serez redirigé vers la page de connexion.
    
    Ce lien expire dans 24h.
    
    Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
    """
    
    html_message = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ 
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;
                display: inline-block;
            }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Bienvenue sur TriMedHaiti</h2>
            <p>Bonjour <strong>{user.nom_complet}</strong>,</p>
            <p>Merci de vous être inscrit. Veuillez cliquer sur le bouton ci-dessous pour activer votre compte :</p>
            <p style="text-align: center;">
                <a href="{verification_link}" class="button">
                    Vérifier mon email
                </a>
            </p>
            <p>Ou copiez ce lien dans votre navigateur :</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            <p>Ce lien expire dans <strong>24 heures</strong>.</p>
            <p>Après vérification, vous serez automatiquement redirigé vers la page de connexion.</p>
            <hr>
            <div class="footer">
                <p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</p>
                <p>&copy; 2025 TriMedHaiti - Tous droits réservés</p>
            </div>
        </div>
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
        print(f" Email envoyé à {user.email} - Status: {response.status_code}")
        return response.status_code == 201
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False