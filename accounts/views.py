from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import ASC, User
from locations.models import Site, ZoneASC, Region, District
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
from dhis2 import Api
import sys
import os

# Configuration DHIS2
DHIS2_URL = "https://dhis2.integratehealth.org/dhis"
DHIS2_USERNAME = "djakpo"
DHIS2_PASSWORD = "Gado@2024"
PROGRAM_ID = "LOHCXZMzADu"


@login_required
def asc_list(request):
    """Liste des ASCs avec filtres"""
    ascs = ASC.objects.all().select_related('site', 'supervisor')

    search = request.GET.get('search')
    if search:
        ascs = ascs.filter(code__icontains=search) | ascs.filter(first_name__icontains=search) | ascs.filter(last_name__icontains=search)

    context = {'ascs': ascs}
    return render(request, 'accounts/asc_list.html', context)


@login_required
def asc_detail(request, pk):
    """Détail d'un ASC"""
    asc = get_object_or_404(ASC.objects.select_related('site', 'supervisor'), pk=pk)
    equipments = asc.equipments.all()
    tickets = asc.repair_tickets.all()

    context = {
        'asc': asc,
        'equipments': equipments,
        'tickets': tickets,
    }
    return render(request, 'accounts/asc_detail.html', context)


@login_required
def asc_create(request):
    """Créer un ASC"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        code = request.POST.get('code')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        site_id = request.POST.get('site')
        supervisor_id = request.POST.get('supervisor')
        start_date = request.POST.get('start_date')
        notes = request.POST.get('notes')

        # Vérifier que le code n'existe pas déjà
        if ASC.objects.filter(code=code).exists():
            messages.error(request, f'Un ASC avec le code "{code}" existe déjà.')
            return redirect('accounts:asc_create')

        # Récupérer les objets liés
        site = get_object_or_404(Site, pk=site_id)

        supervisor = None
        if supervisor_id:
            supervisor = get_object_or_404(User, pk=supervisor_id, role='SUPERVISOR')

        # Créer automatiquement une zone ASC pour cet ASC
        zone_name = f"Zone {first_name} {last_name}"
        zone_code = code  # Le code de la zone est le même que le code de l'ASC

        zone_asc, zone_created = ZoneASC.objects.get_or_create(
            site=site,
            code=zone_code,
            defaults={"name": zone_name}
        )

        # Créer l'ASC
        asc = ASC.objects.create(
            first_name=first_name,
            last_name=last_name,
            code=code,
            gender=gender,
            phone=phone,
            email=email,
            site=site,
            zone_asc=zone_asc,
            supervisor=supervisor,
            start_date=start_date if start_date else None,
            notes=notes,
            is_active=True
        )

        messages.success(request, f'ASC {asc.get_full_name()} ({code}) créé avec succès!')
        return redirect('accounts:asc_detail', pk=asc.pk)

    # GET - Afficher le formulaire
    sites = Site.objects.all().select_related('district__region')
    supervisors = User.objects.filter(role='SUPERVISOR', is_active=True)

    context = {
        'sites': sites,
        'supervisors': supervisors,
        'gender_choices': ASC.GENDER_CHOICES,
    }
    return render(request, 'accounts/asc_create.html', context)


# ============================================================================
# FONCTIONS D'IMPORT DEPUIS DHIS2
# ============================================================================

def export_program_events_reusable(api, program_id, org_unit_id=None, ou_mode="DESCENDANTS"):
    """
    Exporte les événements d'un programme DHIS2 sous une forme réutilisable.
    """
    from datetime import datetime

    # Récupération des métadonnées du programme
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

    # Récupération des événements
    params = {
        "program": program_id,
        "skipPaging": "true",
        "fields": "*"
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

    # Mise à plat des événements
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

    return {
        "export_date": datetime.now().isoformat(),
        "program_id": program_id,
        "program_name": program_name,
        "total_events": len(export_rows),
        "data_elements": data_elements,
        "events_raw": events_raw,
        "events": export_rows
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
    Extrait les valeurs uniques d'un champ admin_org_unit_*
    Retourne: [{"code": "", "name": ""}]
    """
    results = {}

    for event in data.get("events", []):
        raw_value = event.get(field_name)
        parsed = extract_code_name(raw_value)

        if parsed:
            results[parsed["code"]] = parsed

    return list(results.values())


def get_admin_org_unit_regions(data):
    return extract_unique_admin_units(data, "admin_org_unit_region")


def get_admin_org_unit_sites(data):
    return extract_unique_admin_units(data, "admin_org_unit_site")


def get_admin_org_unit_districts(data):
    return extract_unique_admin_units(data, "admin_org_unit_district")


def parse_asc_data(asc_string):
    """
    Parse les données ASC du format DHIS2
    Format: "ID_DHIS2<==>CODE NOM Prénom<==>CODE"
    Exemple: "FAMBTy5PL4t<==>KBINDJ-001 KPIKI Pirenam<==>KBINDJ-001"
    """
    if not asc_string or "<==>" not in asc_string:
        return None

    parts = asc_string.split("<==>")
    if len(parts) < 3:
        return None

    # parts[0] = ID DHIS2 (non utilisé)
    # parts[1] = "CODE NOM Prénom"
    # parts[2] = CODE
    full_info = parts[1].strip()
    code = parts[2].strip()

    # Extraire le code, nom et prénom de la partie full_info
    # Format: "KBINDJ-001 KPIKI Pirenam"
    info_parts = full_info.split(" ", 2)
    if len(info_parts) < 3:
        return None

    _, last_name, first_name = info_parts

    return {
        "code": code,
        "last_name": last_name,
        "first_name": first_name
    }


def get_ascs_from_dhis2(data):
    """
    Extrait la liste unique des ASCs depuis les données DHIS2
    """
    ascs = {}

    for event in data.get("events", []):
        # Récupérer les données ASC
        asc_string = event.get("admin_org_unit_asc")
        if not asc_string:
            continue

        asc_data = parse_asc_data(asc_string)
        if not asc_data:
            continue

        code = asc_data["code"]

        # Récupérer le site associé
        site_data = extract_code_name(event.get("admin_org_unit_site"))

        if code not in ascs:
            ascs[code] = {
                **asc_data,
                "site_code": site_data["code"] if site_data else None
            }

    return list(ascs.values())


# ============================================================================
# VUES DE SYNCHRONISATION
# ============================================================================

@login_required
def sync_organizational_units(request):
    """Synchroniser les unités d'organisation (Régions, Districts, Sites) depuis DHIS2"""
    if request.method != 'POST':
        return redirect('accounts:asc_list')

    # try:
    # Créer une instance API DHIS2
    api = Api(DHIS2_URL, DHIS2_USERNAME, DHIS2_PASSWORD)

    # Exporter les données depuis DHIS2
    data = export_program_events_reusable(api, PROGRAM_ID)

    # Extraire les unités d'organisation
    regions_data = get_admin_org_unit_regions(data)
    districts_data = get_admin_org_unit_districts(data)
    sites_data = get_admin_org_unit_sites(data)

    print(f"DEBUG: {len(regions_data)} régions, {len(districts_data)} districts, {len(sites_data)} sites extraits")

    created_regions = 0
    created_districts = 0
    created_sites = 0

    # Créer les régions
    with transaction.atomic():
        for region_info in regions_data:
            region, created = Region.objects.get_or_create(
                code=region_info["code"],
                defaults={"name": region_info["name"]}
            )
            if created:
                created_regions += 1

    # Créer les districts
    with transaction.atomic():
        for district_info in districts_data:
            # Pour chaque district, on doit trouver sa région
            # On va chercher dans les événements pour trouver la région associée
            region_code = None
            for event in data.get("events", []):
                district_event = extract_code_name(event.get("admin_org_unit_district"))
                if district_event and district_event["code"] == district_info["code"]:
                    region_event = extract_code_name(event.get("admin_org_unit_region"))
                    if region_event:
                        region_code = region_event["code"]
                        break

            if region_code:
                region = Region.objects.filter(code=region_code).first()
                if region:
                    district, created = District.objects.get_or_create(
                        code=district_info["code"],
                        region=region,
                        defaults={"name": district_info["name"]}
                    )
                    if created:
                        created_districts += 1

    # Créer les sites
    with transaction.atomic():
        for site_info in sites_data:
            # Pour chaque site, on doit trouver son district
            district_code = None
            for event in data.get("events", []):
                site_event = extract_code_name(event.get("admin_org_unit_site"))
                if site_event and site_event["code"] == site_info["code"]:
                    district_event = extract_code_name(event.get("admin_org_unit_district"))
                    if district_event:
                        district_code = district_event["code"]
                        break

            if district_code:
                # Trouver le district par code et région
                for event in data.get("events", []):
                    district_event = extract_code_name(event.get("admin_org_unit_district"))
                    if district_event and district_event["code"] == district_code:
                        region_event = extract_code_name(event.get("admin_org_unit_region"))
                        if region_event:
                            region = Region.objects.filter(code=region_event["code"]).first()
                            if region:
                                district = District.objects.filter(code=district_code, region=region).first()
                                if district:
                                    site, created = Site.objects.get_or_create(
                                        code=site_info["code"],
                                        defaults={
                                            "name": site_info["name"],
                                            "district": district
                                        }
                                    )
                                    if created:
                                        created_sites += 1
                                    break

    messages.success(
        request,
        f'Synchronisation réussie: {created_regions} région(s), '
        f'{created_districts} district(s), {created_sites} site(s) créé(s).'
    )

    # except Exception as e:
    #     messages.error(request, f'Erreur lors de la synchronisation: {str(e)}')

    return redirect('accounts:asc_list')


@login_required
def sync_ascs(request):
    """Synchroniser les ASCs depuis DHIS2"""
    if request.method != 'POST':
        return redirect('accounts:asc_list')

    # try:
    # Créer une instance API DHIS2
    api = Api(DHIS2_URL, DHIS2_USERNAME, DHIS2_PASSWORD)

    # Exporter les données depuis DHIS2
    data = export_program_events_reusable(api, PROGRAM_ID)

    # Extraire les ASCs
    ascs_data = get_ascs_from_dhis2(data)

    print(f"DEBUG: {len(ascs_data)} ASCs extraits depuis DHIS2")
    if ascs_data:
        print(f"DEBUG: Premier ASC exemple: {ascs_data[0]}")

    created_ascs = 0
    updated_ascs = 0

    # Créer ou mettre à jour les ASCs
    with transaction.atomic():
        for asc_info in ascs_data:
            code = asc_info["code"]
            site_code = asc_info["site_code"]

            print(f"DEBUG: Traitement ASC {code} avec site_code {site_code}")

            # Trouver le site
            site = None
            if site_code:
                site = Site.objects.filter(code=site_code).first()
                if site:
                    print(f"DEBUG: Site trouvé: {site.name}")
                else:
                    print(f"DEBUG: Site non trouvé pour code {site_code}")

            # Créer ou mettre à jour l'ASC (même sans site)
            asc, created = ASC.objects.update_or_create(
                code=code,
                defaults={
                    "first_name": asc_info["first_name"],
                    "last_name": asc_info["last_name"],
                    "site": site,
                    "phone": "",  # Non disponible dans DHIS2
                    "is_active": True
                }
            )

            print(f"DEBUG: ASC {'créé' if created else 'mis à jour'}: {asc}")

            # Créer automatiquement une zone ASC pour cet ASC
            if site:
                zone_name = f"Zone {asc_info['first_name']} {asc_info['last_name']}"
                zone_code = code  # Le code de la zone est le même que le code de l'ASC (format DHIS2)

                zone, zone_created = ZoneASC.objects.get_or_create(
                    site=site,
                    code=zone_code,
                    defaults={"name": zone_name}
                )

                print(f"DEBUG: Zone {'créée' if zone_created else 'trouvée'}: {zone}")

                # Associer la zone à l'ASC
                asc.zone_asc = zone
                asc.save()

            if created:
                created_ascs += 1
            else:
                updated_ascs += 1

    messages.success(
        request,
        f'Synchronisation réussie: {created_ascs} ASC(s) créé(s), {updated_ascs} ASC(s) mis à jour.'
    )

    # except Exception as e:
    #     messages.error(request, f'Erreur lors de la synchronisation: {str(e)}')

    return redirect('accounts:asc_list')
