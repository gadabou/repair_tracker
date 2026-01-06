from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Equipment, EquipmentHistory
from accounts.models import ASC


@login_required
def equipment_list(request):
    """Liste des équipements"""
    equipments = Equipment.objects.all().select_related('owner')
    context = {'equipments': equipments}
    return render(request, 'assets/list.html', context)


@login_required
def equipment_detail(request, pk):
    """Détail d'un équipement"""
    equipment = get_object_or_404(Equipment.objects.select_related('owner'), pk=pk)
    history = equipment.history.all()
    tickets = equipment.repair_tickets.all()

    context = {
        'equipment': equipment,
        'history': history,
        'tickets': tickets,
    }
    return render(request, 'assets/detail.html', context)


@login_required
def equipment_create(request):
    """Créer un équipement"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        equipment_type = request.POST.get('equipment_type')
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        imei = request.POST.get('imei')
        serial_number = request.POST.get('serial_number')
        owner_id = request.POST.get('owner')
        status = request.POST.get('status', 'FUNCTIONAL')
        acquisition_date = request.POST.get('acquisition_date')
        warranty_expiry_date = request.POST.get('warranty_expiry_date')
        assignment_date = request.POST.get('assignment_date')
        reception_form = request.FILES.get('reception_form')
        notes = request.POST.get('notes')

        # Vérifier que l'IMEI n'existe pas déjà
        if Equipment.objects.filter(imei=imei).exists():
            messages.error(request, f'Un équipement avec l\'IMEI "{imei}" existe déjà.')
            return redirect('assets:create')

        # Récupérer le propriétaire si spécifié
        owner = None
        if owner_id:
            owner = get_object_or_404(ASC, pk=owner_id)

        # Créer l'équipement
        equipment = Equipment.objects.create(
            equipment_type=equipment_type,
            brand=brand,
            model=model,
            imei=imei,
            serial_number=serial_number,
            owner=owner,
            status=status,
            acquisition_date=acquisition_date if acquisition_date else None,
            warranty_expiry_date=warranty_expiry_date if warranty_expiry_date else None,
            assignment_date=assignment_date if assignment_date else None,
            reception_form=reception_form,
            notes=notes
        )

        # Créer un enregistrement d'historique
        EquipmentHistory.objects.create(
            equipment=equipment,
            action='CREATED',
            old_value='',
            new_value=f'{brand} {model}',
            notes=f'Équipement créé',
            created_by=request.user
        )

        # Si un propriétaire est assigné, créer aussi un historique d'assignation
        if owner:
            EquipmentHistory.objects.create(
                equipment=equipment,
                action='ASSIGNED',
                old_value='Non assigné',
                new_value=str(owner),
                notes=f'Équipement assigné à {owner.get_full_name()}',
                created_by=request.user
            )

        messages.success(request, f'Équipement {brand} {model} ({imei}) créé avec succès!')
        return redirect('assets:detail', pk=equipment.pk)

    # GET - Afficher le formulaire
    ascs = ASC.objects.filter(is_active=True).select_related('site')

    context = {
        'equipment_types': Equipment.TYPE_CHOICES,
        'status_choices': Equipment.STATUS_CHOICES,
        'ascs': ascs,
    }
    return render(request, 'assets/create.html', context)


@login_required
def equipment_assign(request, pk):
    """Attribuer un équipement à un ASC"""
    equipment = get_object_or_404(Equipment, pk=pk)

    if request.method == 'POST':
        asc_id = request.POST.get('asc')

        if asc_id:
            new_asc = get_object_or_404(ASC, pk=asc_id)
            old_owner = equipment.owner

            # Mettre à jour le propriétaire
            equipment.owner = new_asc
            equipment.save()

            # Créer un enregistrement d'historique
            EquipmentHistory.objects.create(
                equipment=equipment,
                action='ASSIGNED' if not old_owner else 'TRANSFERRED',
                old_value=str(old_owner) if old_owner else 'Non assigné',
                new_value=str(new_asc),
                notes=f"Équipement {'assigné' if not old_owner else 'transféré'} à {new_asc.get_full_name()}",
                created_by=request.user
            )

            action = 'assigné' if not old_owner else 'transféré'
            messages.success(request, f'Équipement {action} à {new_asc.get_full_name()} avec succès!')
            return redirect('assets:detail', pk=equipment.pk)
        else:
            messages.error(request, 'Veuillez sélectionner un ASC.')

    ascs = ASC.objects.filter(is_active=True).select_related('site')
    context = {
        'equipment': equipment,
        'ascs': ascs,
    }
    return render(request, 'assets/assign.html', context)


@login_required
def asc_assign_equipment(request, asc_pk):
    """Attribuer plusieurs équipements à un ASC"""
    asc = get_object_or_404(ASC, pk=asc_pk)

    if request.method == 'POST':
        equipment_ids = request.POST.getlist('equipment_ids')
        assignment_date = request.POST.get('assignment_date')
        reception_form = request.FILES.get('reception_form')

        if equipment_ids:
            assigned_count = 0
            skipped_count = 0
            for equipment_id in equipment_ids:
                try:
                    equipment = Equipment.objects.get(pk=equipment_id)

                    # VÉRIFICATION CRITIQUE: Un équipement ne peut appartenir qu'à un seul ASC
                    if equipment.owner is not None:
                        skipped_count += 1
                        messages.warning(
                            request,
                            f'Équipement {equipment.imei} ignoré - déjà attribué à {equipment.owner.get_full_name()}'
                        )
                        continue

                    # Mettre à jour l'équipement
                    equipment.owner = asc
                    if assignment_date:
                        equipment.assignment_date = assignment_date
                    if reception_form and assigned_count == 0:  # Save form only for first equipment
                        equipment.reception_form = reception_form
                    equipment.save()

                    # Créer un enregistrement d'historique
                    EquipmentHistory.objects.create(
                        equipment=equipment,
                        action='ASSIGNED',
                        old_value='Non assigné',
                        new_value=str(asc),
                        notes=f"Équipement assigné à {asc.get_full_name()}",
                        created_by=request.user
                    )
                    assigned_count += 1
                except Equipment.DoesNotExist:
                    continue

            if assigned_count > 0:
                messages.success(request, f'{assigned_count} équipement(s) attribué(s) à {asc.get_full_name()} avec succès!')
                if skipped_count > 0:
                    messages.info(request, f'{skipped_count} équipement(s) déjà attribué(s) ont été ignorés.')
                return redirect('accounts:asc_detail', pk=asc.pk)
            else:
                messages.error(request, 'Aucun équipement valide sélectionné.')
        else:
            messages.error(request, 'Veuillez sélectionner au moins un équipement.')

    # Récupérer les équipements disponibles (sans propriétaire ou avec statut fonctionnel)
    available_equipments = Equipment.objects.filter(
        owner__isnull=True
    ).order_by('-created_at')

    context = {
        'asc': asc,
        'available_equipments': available_equipments,
    }
    return render(request, 'assets/asc_assign_equipment.html', context)
