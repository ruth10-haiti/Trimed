import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('BREVO_API_KEY')


if not api_key:
    print(" BREVO_API_KEY non définie dans .env")
    exit(1)

url = "https://api.brevo.com/v3/account"
headers = {
    "api-key": api_key,
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print(" Clé API Brevo valide !")
else:
    print(" Clé API invalide")