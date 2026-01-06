from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import models
from .models import RepairTicket, TicketEvent, TicketComment, Issue, DelayAlertRecipient, DelayAlertLog, ProblemType
from assets.models import Equipment
from accounts.models import User


@login_required
def ticket_list(request):
    """Liste des tickets avec filtres"""
    tickets = RepairTicket.objects.all().select_related('equipment', 'asc', 'current_holder')

    # Filtres
    status = request.GET.get('status')
    stage = request.GET.get('stage')
    search = request.GET.get('search')

    if status:
        tickets = tickets.filter(status=status)
    if stage:
        tickets = tickets.filter(current_stage=stage)
    if search:
        tickets = tickets.filter(ticket_number__icontains=search)

    context = {
        'tickets': tickets,
        'status_choices': RepairTicket.STATUS_CHOICES,
        'stage_choices': RepairTicket.STAGE_CHOICES,
    }
    return render(request, 'tickets/list.html', context)


@login_required
def ticket_detail(request, pk):
    """Détail d'un ticket avec timeline"""
    ticket = get_object_or_404(RepairTicket.objects.select_related('equipment', 'asc', 'current_holder'), pk=pk)
    events = ticket.events.all().select_related('user').order_by('timestamp')
    comments = ticket.comments.all().select_related('user').order_by('created_at')
    issues = ticket.issues.all()

    context = {
        'ticket': ticket,
        'events': events,
        'comments': comments,
        'issues': issues,
    }
    return render(request, 'tickets/detail.html', context)


@login_required
def ticket_create(request):
    """Créer un nouveau ticket (superviseurs uniquement)"""
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment')
        asc_id = request.POST.get('asc')
        problem_description = request.POST.get('problem_description')

        equipment = get_object_or_404(Equipment, pk=equipment_id)

        # Utiliser l'ASC du formulaire, sinon celui de l'équipement
        from accounts.models import ASC
        if asc_id:
            asc = get_object_or_404(ASC, pk=asc_id)
        else:
            asc = equipment.owner

        ticket = RepairTicket.objects.create(
            equipment=equipment,
            asc=asc,
            created_by=request.user,
            initial_problem_description=problem_description,
            current_stage='SUPERVISOR',
            current_holder=request.user
        )

        # Créer les issues
        problem_type_ids = request.POST.getlist('problem_types')
        issue_description = request.POST.get('issue_description', '')

        if problem_type_ids:
            for problem_type_id in problem_type_ids:
                problem_type = get_object_or_404(ProblemType, pk=problem_type_id)
                Issue.objects.create(
                    ticket=ticket,
                    problem_type=problem_type,
                    description=issue_description
                )

        # Créer l'événement de création
        TicketEvent.objects.create(
            ticket=ticket,
            event_type='CREATED',
            user=request.user,
            from_role='SUPERVISOR',
            to_role='SUPERVISOR',
            comment='Ticket créé'
        )

        equipment.status = 'UNDER_REPAIR'
        equipment.save()

        messages.success(request, f'Ticket {ticket.ticket_number} créé avec succès!')
        return redirect('tickets:detail', pk=ticket.pk)

    # Récupérer tous les types de problèmes actifs et les grouper par catégorie
    problem_types = ProblemType.objects.filter(is_active=True).order_by('category', 'display_order', 'name')

    # Grouper par catégorie
    hardware_problems = problem_types.filter(category='HARDWARE')
    software_problems = problem_types.filter(category='SOFTWARE')
    other_problems = problem_types.filter(category='OTHER')

    equipments = Equipment.objects.filter(status__in=['FAULTY', 'FUNCTIONAL']).select_related('owner')
    context = {
        'equipments': equipments,
        'hardware_problems': hardware_problems,
        'software_problems': software_problems,
        'other_problems': other_problems,
    }
    return render(request, 'tickets/create.html', context)


@login_required
def ticket_receive(request, pk):
    """Confirmer la réception d'un ticket"""
    ticket = get_object_or_404(RepairTicket, pk=pk)

    if request.method == 'POST':
        comment = request.POST.get('comment', '')

        TicketEvent.objects.create(
            ticket=ticket,
            event_type='RECEIVED',
            user=request.user,
            from_role=ticket.current_stage,
            to_role=ticket.current_stage,
            comment=comment,
            timestamp=timezone.now()
        )

        ticket.current_holder = request.user
        ticket.status = 'IN_PROGRESS'
        ticket.save()

        messages.success(request, 'Réception confirmée!')
        return redirect('tickets:detail', pk=ticket.pk)

    return render(request, 'tickets/receive.html', {'ticket': ticket})


@login_required
def ticket_send(request, pk):
    """Envoyer un ticket à l'étape suivante"""
    from accounts.models import User

    ticket = get_object_or_404(RepairTicket, pk=pk)

    # Définir les transitions possibles selon l'étape actuelle
    workflow_transitions = {
        'SUPERVISOR': ['PROGRAM'],
        'PROGRAM': ['LOGISTICS'],
        'LOGISTICS': ['REPAIRER', 'ESANTE'],
        'REPAIRER': ['RETURNING_LOGISTICS'],
        'ESANTE': ['RETURNING_LOGISTICS'],
        'RETURNING_LOGISTICS': ['RETURNING_PROGRAM'],
        'RETURNING_PROGRAM': ['RETURNING_SUPERVISOR'],
        'RETURNING_SUPERVISOR': ['RETURNED_ASC'],
    }

    # Filtrer les choix possibles selon l'étape actuelle
    possible_next_stages = workflow_transitions.get(ticket.current_stage, [])
    stage_choices = [(stage, label) for stage, label in RepairTicket.STAGE_CHOICES if stage in possible_next_stages]

    if request.method == 'POST':
        to_role = request.POST.get('to_role')
        recipient_id = request.POST.get('recipient')
        comment = request.POST.get('comment', '')

        # Vérifier que la transition est valide
        if to_role not in possible_next_stages:
            messages.error(request, 'Transition invalide!')
            return redirect('tickets:detail', pk=ticket.pk)

        # Récupérer le destinataire
        recipient = None
        if recipient_id and to_role != 'RETURNED_ASC':
            try:
                recipient = User.objects.get(pk=recipient_id)
            except User.DoesNotExist:
                messages.error(request, 'Destinataire invalide!')
                return redirect('tickets:send', pk=ticket.pk)

        TicketEvent.objects.create(
            ticket=ticket,
            event_type='SENT',
            user=request.user,
            from_role=ticket.current_stage,
            to_role=to_role,
            comment=comment,
            timestamp=timezone.now()
        )

        ticket.current_stage = to_role
        ticket.current_holder = None  # Sera défini à la réception

        # Mettre à jour le statut si on retourne l'équipement
        if to_role.startswith('RETURNING'):
            ticket.status = 'RETURNING'

        # Clôturer le ticket si retourné à l'ASC
        if to_role == 'RETURNED_ASC':
            ticket.status = 'CLOSED'
            ticket.closed_date = timezone.now()
            ticket.equipment.status = 'FUNCTIONAL'
            ticket.equipment.save()

        ticket.save()

        # Notifier le destinataire (optionnel, sera implémenté dans la commande de rappel)
        destination_name = dict(RepairTicket.STAGE_CHOICES)[to_role]
        if recipient:
            messages.success(request, f'Ticket envoyé à {recipient.get_full_name()} ({destination_name})!')
        else:
            messages.success(request, f'Ticket envoyé à {destination_name}!')

        return redirect('tickets:detail', pk=ticket.pk)

    context = {
        'ticket': ticket,
        'stage_choices': stage_choices,
        'possible_next_stages': possible_next_stages,
    }
    return render(request, 'tickets/send.html', context)


@login_required
def ticket_mark_repaired(request, pk):
    """Marquer un ticket comme réparé"""
    ticket = get_object_or_404(RepairTicket, pk=pk)

    if request.method == 'POST':
        resolution_notes = request.POST.get('resolution_notes', '')

        # Mettre à jour le ticket
        ticket.status = 'REPAIRED'
        ticket.repair_completed_date = timezone.now()
        ticket.resolution_notes = resolution_notes
        ticket.save()

        # Créer un événement
        TicketEvent.objects.create(
            ticket=ticket,
            event_type='REPAIRED',
            user=request.user,
            from_role=ticket.current_stage,
            to_role=ticket.current_stage,
            comment=f'Réparation terminée. {resolution_notes}',
            timestamp=timezone.now()
        )

        messages.success(request, 'Réparation marquée comme terminée! Vous pouvez maintenant renvoyer l\'équipement.')
        return redirect('tickets:detail', pk=ticket.pk)

    context = {'ticket': ticket}
    return render(request, 'tickets/mark_repaired.html', context)


@login_required
def ticket_add_comment(request, pk):
    """Ajouter un commentaire à un ticket"""
    ticket = get_object_or_404(RepairTicket, pk=pk)

    if request.method == 'POST':
        comment_text = request.POST.get('comment')

        TicketComment.objects.create(
            ticket=ticket,
            user=request.user,
            comment=comment_text
        )

        messages.success(request, 'Commentaire ajouté!')
        return redirect('tickets:detail', pk=ticket.pk)

    return redirect('tickets:detail', pk=ticket.pk)


@login_required
def ticket_cancel(request, pk):
    """Annuler un ticket"""
    ticket = get_object_or_404(RepairTicket, pk=pk)

    # Vérifier que le ticket n'est pas déjà clôturé ou annulé
    if ticket.status in ['CLOSED', 'CANCELLED']:
        messages.error(request, f'Ce ticket est déjà {ticket.get_status_display().lower()}!')
        return redirect('tickets:detail', pk=ticket.pk)

    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')

        if not cancellation_reason:
            messages.error(request, 'Veuillez fournir une raison pour l\'annulation.')
            return render(request, 'tickets/cancel.html', {'ticket': ticket})

        # Mettre à jour le ticket
        ticket.status = 'CANCELLED'
        ticket.cancelled_date = timezone.now()
        ticket.cancellation_reason = cancellation_reason
        ticket.save()

        # Créer un événement d'annulation
        TicketEvent.objects.create(
            ticket=ticket,
            event_type='CANCELLED',
            user=request.user,
            from_role=ticket.current_stage,
            to_role=ticket.current_stage,
            comment=f'Ticket annulé. Raison: {cancellation_reason}',
            timestamp=timezone.now()
        )

        # Remettre l'équipement en panne (pas en réparation)
        ticket.equipment.status = 'FAULTY'
        ticket.equipment.save()

        messages.success(request, f'Ticket {ticket.ticket_number} annulé avec succès!')
        return redirect('tickets:detail', pk=ticket.pk)

    context = {'ticket': ticket}
    return render(request, 'tickets/cancel.html', context)


@login_required
def alert_recipients_config(request):
    """Configuration des destinataires d'alertes de dépassement de délai"""
    # Vérifier que l'utilisateur est administrateur
    if not request.user.is_staff and not request.user.is_admin_role():
        messages.error(request, "Vous n'avez pas les droits nécessaires pour accéder à cette page.")
        return redirect('dashboard:home')

    if request.method == 'POST':
        # Récupérer les utilisateurs sélectionnés
        user_ids = request.POST.getlist('users')

        # Supprimer les anciens destinataires
        DelayAlertRecipient.objects.all().delete()

        # Créer les nouveaux destinataires
        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                email = request.POST.get(f'email_{user_id}', user.email)
                recipient_type = request.POST.get(f'type_{user_id}', 'PRIMARY')

                DelayAlertRecipient.objects.create(
                    user=user,
                    email=email,
                    recipient_type=recipient_type,
                    is_active=True
                )
            except User.DoesNotExist:
                continue

        messages.success(request, 'Configuration des destinataires mise à jour avec succès!')
        return redirect('tickets:alert_recipients_config')

    # Récupérer les destinataires actuels
    current_recipients = DelayAlertRecipient.objects.all().select_related('user')

    # Récupérer tous les utilisateurs pour la sélection
    all_users = User.objects.filter(is_active=True).order_by('last_name', 'first_name')

    # Récupérer l'historique des alertes
    recent_alerts = DelayAlertLog.objects.select_related('ticket').order_by('-sent_at')[:20]

    context = {
        'current_recipients': current_recipients,
        'all_users': all_users,
        'recent_alerts': recent_alerts,
    }
    return render(request, 'tickets/alert_recipients_config.html', context)


@login_required
def search_users_api(request):
    """API pour la recherche d'utilisateurs (autocomplétion)"""
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'results': []})

    users = User.objects.filter(
        is_active=True
    ).filter(
        models.Q(first_name__icontains=query) |
        models.Q(last_name__icontains=query) |
        models.Q(email__icontains=query)
    ).order_by('last_name', 'first_name')[:10]

    results = [{
        'id': user.id,
        'text': f"{user.get_full_name()} ({user.get_role_display()})",
        'email': user.email or ''
    } for user in users]

    return JsonResponse({'results': results})


@login_required
def toggle_recipient_status(request, pk):
    """Activer/désactiver un destinataire d'alertes"""
    if not request.user.is_staff and not request.user.is_admin_role():
        return JsonResponse({'error': 'Permission refusée'}, status=403)

    recipient = get_object_or_404(DelayAlertRecipient, pk=pk)
    recipient.is_active = not recipient.is_active
    recipient.save()

    return JsonResponse({
        'success': True,
        'is_active': recipient.is_active
    })
