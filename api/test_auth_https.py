import requests
from requests.auth import HTTPBasicAuth
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configuration avec HTTPS
url_http = "http://dhis2.integratehealth.org/dhis"
url_https = "https://dhis2.integratehealth.org/dhis"
username = "djakpo"
password = "Gado@2024"

# Test avec HTTP
print("=== TEST AVEC HTTP ===")
api_url = f"{url_http}/api/me"
response_http = requests.get(api_url, auth=HTTPBasicAuth(username, password), timeout=10)
print(f"Status code: {response_http.status_code}")
print(f"Content-Type: {response_http.headers.get('Content-Type', 'Non défini')}")
if 'json' in response_http.headers.get('Content-Type', ''):
    print("✓ HTTP fonctionne!")
else:
    print("✗ HTTP ne fonctionne pas - Page HTML reçue")

# Test avec HTTPS
print("\n=== TEST AVEC HTTPS ===")
api_url = f"{url_https}/api/me"
try:
    response_https = requests.get(api_url, auth=HTTPBasicAuth(username, password), verify=False, timeout=10)
    print(f"Status code: {response_https.status_code}")
    print(f"Content-Type: {response_https.headers.get('Content-Type', 'Non défini')}")

    if response_https.status_code == 200:
        if 'application/json' in response_https.headers.get('Content-Type', ''):
            print("✓ HTTPS fonctionne!")
            data = response_https.json()
            print(f"Utilisateur connecté: {data.get('name', 'Inconnu')}")
            print(f"Email: {data.get('email', 'N/A')}")
        else:
            print("✗ HTTPS ne fonctionne pas - Page HTML reçue")
            print("Response:", response_https.text[:200])
    else:
        print(f"✗ Erreur HTTP {response_https.status_code}")

except requests.exceptions.SSLError as e:
    print(f"✗ Erreur SSL: {e}")
except requests.exceptions.Timeout:
    print("✗ Timeout de connexion")
except Exception as e:
    print(f"✗ Erreur: {e}")
