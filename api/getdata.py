import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import json
from datetime import datetime

from dhis2 import Api

# Configuration
url = "https://dhis2.integratehealth.org/dhis"
username = "djakpo"
password = "Gado@2024"
api = Api(url, username, password)

# ID du programme "admin authorized orgUnits"
PROGRAM_ID = "LOHCXZMzADu"

print("=" * 80)
print("EXPORT DES ÉVÉNEMENTS DU PROGRAMME 'admin authorized orgUnits'")
print("=" * 80)

# Étape 0: Rechercher l'unité d'organisation "Togo"
print("\n[0/4] Recherche de l'unité d'organisation...")
print("  Info: Récupération de tous les événements sans filtre d'organisation...")
ORG_UNIT_ID = None

# Étape 1: Récupérer les métadonnées du programme
print("\n[1/3] Récupération des métadonnées du programme...")
try:
    program_response = api.get(
        f"programs/{PROGRAM_ID}",
        params={
            "fields": "id,name,programStages[id,name,programStageDataElements[dataElement[id,code,name,valueType]]]"
        }
    )

    if program_response.status_code == 200:
        program_data = program_response.json()
        print(f"✓ Programme: {program_data.get('name')}")

        # Extraire les data elements
        data_elements = {}
        for stage in program_data.get('programStages', []):
            print(f"  - Stage: {stage.get('name')}")
            for psde in stage.get('programStageDataElements', []):
                de = psde.get('dataElement', {})
                data_elements[de.get('id')] = {
                    'code': de.get('code'),
                    'name': de.get('name'),
                    'valueType': de.get('valueType')
                }

        print(f"✓ {len(data_elements)} éléments de données trouvés")
    else:
        print(f"✗ Erreur: {program_response.status_code}")
        exit(1)

except Exception as e:
    print(f"✗ Erreur: {e}")
    exit(1)

# Étape 2: Récupérer les événements
print("\n[2/3] Récupération des événements...")
try:
    # Construire les paramètres de requête
    params = {
        "program": PROGRAM_ID,
        "skipPaging": "true",
        "fields": "*"
    }

    # Ajouter l'org unit seulement si trouvée
    if ORG_UNIT_ID:
        params["orgUnit"] = ORG_UNIT_ID
        params["ouMode"] = "DESCENDANTS"  # Inclure les sous-unités

    print(f"  Paramètres de recherche: {params}")

    events_response = api.get("events", params=params)

    if events_response.status_code == 200:
        events_data = events_response.json()
        events = events_data.get('events', [])
        print(f"✓ {len(events)} événements récupérés")
    else:
        print(f"✗ Erreur: {events_response.status_code}")
        print(f"Response: {events_response.text[:500]}")
        exit(1)

except Exception as e:
    print(f"✗ Erreur: {e}")
    exit(1)

# Étape 3: Exporter les données
print("\n[3/3] Export des données...")

# Préparer les données pour l'export
export_data = []
for event in events:
    row = {
        'event_id': event.get('event'),
        'event_date': event.get('eventDate'),
        'status': event.get('status'),
        'org_unit': event.get('orgUnit'),
        'org_unit_name': event.get('orgUnitName', '')
    }

    # Ajouter les valeurs des data elements
    for data_value in event.get('dataValues', []):
        de_id = data_value.get('dataElement')
        value = data_value.get('value')

        if de_id in data_elements:
            de_code = data_elements[de_id]['code']
            row[de_code] = value

    export_data.append(row)

# Afficher un aperçu
print(f"\n✓ {len(export_data)} lignes préparées pour l'export")
print("\nAperçu des 5 premiers événements:")

print("-" * 80)

for i, row in enumerate(export_data[:5]):
    print(f"\nÉvénement {i+1}:")
    for key, value in row.items():
        if value:  # N'afficher que les champs non vides
            print(f"  {key}: {value}")

# Export en JSON
json_filename = f"dhis2_events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
print(f"\n[4/4] Export en JSON: {json_filename}")

try:
    # Créer la structure JSON
    export_json = {
        "export_date": datetime.now().isoformat(),
        "program_id": PROGRAM_ID,
        "program_name": "admin authorized orgUnits",
        "total_events": len(export_data),
        "events": export_data
    }

    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(export_json, jsonfile, ensure_ascii=False, indent=2)

    print(f"✓ Export réussi: {json_filename}")
    print(f"✓ {len(export_data)} événements exportés")

except Exception as e:
    print(f"✗ Erreur lors de l'export JSON: {e}")

print("\n" + "=" * 80)
print("EXPORT TERMINÉ")
print("=" * 80)



from datetime import datetime

def export_program_events_reusable(api, program_id, org_unit_id=None, ou_mode="DESCENDANTS"):
    """
    Exporte les événements d'un programme DHIS2 sous une forme réutilisable.

    Retour:
    {
      "export_date": "...",
      "program_id": "...",
      "program_name": "...",
      "total_events": int,
      "data_elements": {de_id: {"code":..., "name":..., "valueType":...}},
      "events_raw": [...],         # événements DHIS2 bruts (optionnel mais utile)
      "events": [...],             # événements plats (row) avec keys = dataElement.code
    }
    """

    # -----------------------------
    # 1) Récupération des métadonnées du programme
    # -----------------------------
    program_response = api.get(
        f"programs/{program_id}",
        params={
            "fields": "id,name,programStages[id,name,programStageDataElements[dataElement[id,code,name,valueType]]]"
        }
    )

    if program_response.status_code != 200:
        raise RuntimeError(
            f"Erreur récupération programme {program_id}: "
            f"{program_response.status_code} - {program_response.text[:500]}"
        )

    program_data = program_response.json()
    program_name = program_data.get("name", "")

    # Mapping data elements: de_id -> {code,name,valueType}
    data_elements = {}
    for stage in program_data.get("programStages", []):
        for psde in stage.get("programStageDataElements", []):
            de = psde.get("dataElement", {})
            de_id = de.get("id")
            if de_id:
                data_elements[de_id] = {
                    "code": de.get("code"),
                    "name": de.get("name"),
                    "valueType": de.get("valueType")
                }

    # -----------------------------
    # 2) Récupération des événements
    # -----------------------------
    params = {
        "program": program_id,
        "skipPaging": "true",
        "fields": "*"   # tu peux réduire si besoin
    }

    if org_unit_id:
        params["orgUnit"] = org_unit_id
        params["ouMode"] = ou_mode

    events_response = api.get("events", params=params)

    if events_response.status_code != 200:
        raise RuntimeError(
            f"Erreur récupération events du programme {program_id}: "
            f"{events_response.status_code} - {events_response.text[:500]}"
        )

    events_data = events_response.json()
    events_raw = events_data.get("events", [])

    # -----------------------------
    # 3) Mise à plat des événements (row) avec les codes des dataElements
    # -----------------------------
    export_rows = []

    for event in events_raw:
        row = {
            "event_id": event.get("event"),
            "event_date": event.get("eventDate"),
            "status": event.get("status"),
            "org_unit": event.get("orgUnit"),
            "org_unit_name": event.get("orgUnitName", "")
        }

        for dv in event.get("dataValues", []):
            de_id = dv.get("dataElement")
            value = dv.get("value")

            meta = data_elements.get(de_id)
            if meta and meta.get("code"):
                row[meta["code"]] = value

        export_rows.append(row)

    # -----------------------------
    # 4) Structure de retour
    # -----------------------------
    return {
        "export_date": datetime.now().isoformat(),
        "program_id": program_id,
        "program_name": program_name,
        "total_events": len(export_rows),
        "data_elements": data_elements,
        "events_raw": events_raw,     # utile si tu veux debug ou enrichir
        "events": export_rows         # c'est CE QUE tes fonctions précédentes consommeront
    }



def extract_code_name(value):
    """
    Transforme 'CODE<==>NAME' en dict {'code': CODE, 'name': NAME}
    """
    if not value or "<==>" not in value:
        return None

    code, name = value.split("<==>", 1)
    return {
        "code": code.strip(),
        "name": name.strip()
    }


def extract_unique_admin_units(data, field_name):
    """
    Extrait les valeurs uniques d’un champ admin_org_unit_*
    Retourne: [{"code": "", "name": ""}]
    """
    results = {}

    for event in data.get("events", []):
        raw_value = event.get(field_name)
        parsed = extract_code_name(raw_value)

        if parsed:
            results[parsed["code"]] = parsed  # évite les doublons par code

    return list(results.values())

def get_admin_org_unit_regions(data):
    return extract_unique_admin_units(data, "admin_org_unit_region")


def get_admin_org_unit_sites(data):
    return extract_unique_admin_units(data, "admin_org_unit_site")


def get_admin_org_unit_districts(data):
    return extract_unique_admin_units(data, "admin_org_unit_district")




data = export_program_events_reusable(api, "LOHCXZMzADu")

regions = get_admin_org_unit_regions(data)     # s’appuie sur data["events"]
sites = get_admin_org_unit_sites(data)
districts = get_admin_org_unit_districts(data)

print("================================================================================================================\n")
print("regions", regions)
print("sites", sites)
print("districts", districts)



