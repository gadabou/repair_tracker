import requests
from requests.auth import HTTPBasicAuth

# Configuration
url = "http://dhis2.integratehealth.org/dhis"
username = "djakpo"
password = "Gado@2024"

# Test 1: Connexion simple avec requests
print("=== TEST 1: Authentification avec requests ===")
api_url = f"{url}/api/me"
response = requests.get(api_url, auth=HTTPBasicAuth(username, password))

print(f"Status code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type', 'Non défini')}")

if response.status_code == 200:
    if 'application/json' in response.headers.get('Content-Type', ''):
        print("✓ Authentification réussie!")
        data = response.json()
        print(f"Utilisateur connecté: {data.get('name', 'Inconnu')}")
    else:
        print("✗ La réponse n'est pas du JSON")
        print("HTML reçu (premiers 200 caractères):", response.text[:200])
else:
    print(f"✗ Erreur HTTP {response.status_code}")
    print("Response:", response.text[:200])

print("\n=== TEST 2: Test avec l'API dhis2 ===")
try:
    from dhis2 import Api
    api = Api(url, username, password)

    # Test simple avec l'endpoint /api/me
    me_response = api.get("me")
    print(f"Status code: {me_response.status_code}")

    if me_response.status_code == 200:
        try:
            me_data = me_response.json()
            print("✓ API dhis2 fonctionne!")
            print(f"Utilisateur: {me_data.get('name', 'Inconnu')}")
        except:
            print("✗ Impossible de parser le JSON")
            print("Response:", me_response.text[:200])
    else:
        print(f"✗ Erreur {me_response.status_code}")

except Exception as e:
    print(f"✗ Erreur lors de l'utilisation de l'API dhis2: {e}")
