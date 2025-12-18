from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from tickets.models import RepairTicket
from assets.models import Equipment
from accounts.models import ASC


def home_redirect(request):
    """Redirige vers le dashboard ou la page de login"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('login')


@login_required
def dashboard_home(request):
    """Page d'accueil du dashboard avec statistiques"""

    # Statistiques globales
    total_tickets = RepairTicket.objects.count()
    open_tickets = RepairTicket.objects.filter(status='OPEN').count()
    in_progress_tickets = RepairTicket.objects.filter(status='IN_PROGRESS').count()
    repaired_tickets = RepairTicket.objects.filter(status='REPAIRED').count()
    closed_tickets = RepairTicket.objects.filter(status='CLOSED').count()

    # Tickets par couleur (délai)
    all_tickets = RepairTicket.objects.exclude(status='CLOSED')
    red_tickets = [t for t in all_tickets if t.get_delay_days() > 14]
    yellow_tickets = [t for t in all_tickets if 7 < t.get_delay_days() <= 14]
    green_tickets = [t for t in all_tickets if t.get_delay_days() <= 7]

    # Durée moyenne de traitement
    closed_with_dates = RepairTicket.objects.filter(
        status='CLOSED',
        closed_date__isnull=False
    )
    avg_duration = None
    if closed_with_dates.exists():
        durations = [(t.closed_date - t.initial_send_date).days for t in closed_with_dates]
        avg_duration = sum(durations) / len(durations)

    # Top 5 des points de blocage
    blocked_tickets = [t for t in all_tickets if t.is_blocked()]
    stage_counts = {}
    for ticket in blocked_tickets:
        stage = ticket.get_current_stage_display()
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    top_blockages = sorted(stage_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Tickets rouges récents
    recent_red_tickets = sorted(red_tickets, key=lambda t: t.get_delay_days(), reverse=True)[:10]

    # Statistiques par étape
    stage_stats = {}
    for stage, label in RepairTicket.STAGE_CHOICES:
        stage_stats[label] = RepairTicket.objects.filter(current_stage=stage).count()

    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'repaired_tickets': repaired_tickets,
        'closed_tickets': closed_tickets,
        'red_count': len(red_tickets),
        'yellow_count': len(yellow_tickets),
        'green_count': len(green_tickets),
        'avg_duration': round(avg_duration, 1) if avg_duration else None,
        'top_blockages': top_blockages,
        'recent_red_tickets': recent_red_tickets,
        'stage_stats': stage_stats,
        'total_ascs': ASC.objects.filter(is_active=True).count(),
        'total_equipment': Equipment.objects.count(),
    }

    return render(request, 'dashboard/home.html', context)
