from os.path import split
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

from dhis2 import Api
url="https://dhis2.integratehealth.org/dhis"  # Changé de HTTP à HTTPS
username="djakpo"
password="Gado@2024"
api = Api(url, username, password)
pageSize = 1000000
#optionApi =f"https://dhis2.integratehealth.org/dhis/api/options.json?paging=false&pageSize=10&filter=optionSet.id:eq:uOKgQa2W8tn&fields=id,code,name,optionSet"


response = api.get(
    "options",
    params={
        "paging":False,
        "pageSize":pageSize,
        "filter":"optionSet.id:eq:uOKgQa2W8tn",
        "fields":"id,code,name,optionSet"
    }
)

print("=== PREMIERE REQUETE: OPTIONS ===")
print("Status code:", response.status_code)
if response.status_code != 200:
    print("Erreur HTTP:", response.status_code)
    print("Response:", response.text[:500])
    exit(1)

try:
    res = response.json()
    print("✓ JSON parsé avec succès")
    print(f"Nombre d'options: {len(res.get('options', []))}")
except Exception as e:
    print(f"✗ Erreur lors du parsing JSON: {e}")
    print("Response:", response.text[:500])
    exit(1)


# Cette requête échoue avec une erreur 404 - endpoint non trouvé ou paramètres incorrects
# Commentée pour permettre l'exécution du reste du script
"""
ih_org_units = api.get(
    "programStageDataElements",
    params={
        "filter": [
            "programStage.program.id:eq:LOHCXZMzADu",
            "dataElement.code:eq:admin_org_unit_site"
        ],
        "fields": (
            "id,"
            "dataElement[id,code,name,valueType],"
            "programStage[id,name]"
        ),
        "paging": "false"
    }
)

print("\n=== DEUXIEME REQUETE: PROGRAM STAGE DATA ELEMENTS ===")
print("Status code:", ih_org_units.status_code)
if ih_org_units.status_code != 200:
    print("Erreur HTTP:", ih_org_units.status_code)
    print("Response:", ih_org_units.text[:500])
    exit(1)

try:
    org_units_data = ih_org_units.json()
    print("✓ JSON parsé avec succès")
    print("Données:", org_units_data)
except Exception as e:
    print(f"✗ Erreur lors du parsing JSON: {e}")
    print("Response text (first 500 chars):", ih_org_units.text[:500])
    exit(1)
"""

print("\n=== AFFICHAGE DES OPTIONS ===")
optionsList = res.get("options", [])
print(f"Total d'options: {len(optionsList)}\n")

for option in optionsList:
    code = option.get("code", "")
    name = option.get("name", "").split()[1]
    firstname = option.get("name", "").split()[2]

    # name = nameWithCode.split(code + " ")[0] if code in nameWithCode else nameWithCode

    print(f"Code: {code}")
    print(f"Name: {name} {firstname}")
    print("---")