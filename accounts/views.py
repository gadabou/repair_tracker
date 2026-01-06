from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ASC, User
from locations.models import Site, ZoneASC


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
        zone_asc_id = request.POST.get('zone_asc')
        supervisor_id = request.POST.get('supervisor')
        start_date = request.POST.get('start_date')
        notes = request.POST.get('notes')

        # Vérifier que le code n'existe pas déjà
        if ASC.objects.filter(code=code).exists():
            messages.error(request, f'Un ASC avec le code "{code}" existe déjà.')
            return redirect('accounts:asc_create')

        # Récupérer les objets liés
        site = get_object_or_404(Site, pk=site_id)
        zone_asc = None
        if zone_asc_id:
            zone_asc = get_object_or_404(ZoneASC, pk=zone_asc_id)

        supervisor = None
        if supervisor_id:
            supervisor = get_object_or_404(User, pk=supervisor_id, role='SUPERVISOR')

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
    sites = Site.objects.all().select_related('commune__district__region')
    zones_asc = ZoneASC.objects.all().select_related('site__commune')
    supervisors = User.objects.filter(role='SUPERVISOR', is_active=True)

    context = {
        'sites': sites,
        'zones_asc': zones_asc,
        'supervisors': supervisors,
        'gender_choices': ASC.GENDER_CHOICES,
    }
    return render(request, 'accounts/asc_create.html', context)
