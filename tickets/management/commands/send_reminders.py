# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from tickets.models import RepairTicket


class Command(BaseCommand):
    help = 'Envoie des rappels par email pour les tickets en attente depuis trop longtemps'

    def handle(self, *args, **options):
        # Récupérer tous les tickets non clôturés avec un détenteur
        tickets = RepairTicket.objects.filter(
            status__in=['OPEN', 'IN_PROGRESS', 'REPAIRED', 'RETURNING'],
            current_holder__isnull=False
        ).select_related('current_holder', 'equipment', 'asc')

        reminders_sent = 0

        for ticket in tickets:
            days = ticket.get_time_at_current_stage()

            # Envoyer rappel à 7 et 14 jours
            if days == 7 or days == 14:
                # Déterminer le niveau d'urgence
                urgency = "ATTENTION" if days == 7 else "URGENT"
                color = "jaune" if days == 7 else "rouge"

                # Créer le message
                subject = f"[{urgency}] Rappel: Ticket {ticket.ticket_number} - {days} jours"

                message = f"""
Bonjour {ticket.current_holder.get_full_name()},

Ceci est un rappel automatique concernant le ticket de réparation suivant:

TICKET: {ticket.ticket_number}
ÉQUIPEMENT: {ticket.equipment}
ASC: {ticket.asc.get_full_name()}
ÉTAPE ACTUELLE: {ticket.get_current_stage_display()}

L'équipement est dans votre département depuis {days} jours.
⚠️ ÉTAT: {color.upper()}

{
'Merci de traiter ce ticket rapidement et de l\'envoyer à l\'étape suivante.' if days == 7
else 'Ce ticket nécessite une attention URGENTE. Veuillez le traiter immédiatement.'
}

Description du problème:
{ticket.initial_problem_description}

Vous pouvez accéder au ticket ici:
{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/tickets/{ticket.pk}/

Cordialement,
Système de suivi des réparations - Repair Tracker
                """.strip()

                # Envoyer l'email
                try:
                    if ticket.current_holder.email:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@repairtracker.com',
                            recipient_list=[ticket.current_holder.email],
                            fail_silently=False,
                        )
                        reminders_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Rappel envoyé à {ticket.current_holder.get_full_name()} '
                                f'pour le ticket {ticket.ticket_number} ({days} jours)'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Pas d\'email pour {ticket.current_holder.get_full_name()} '
                                f'(ticket {ticket.ticket_number})'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Erreur lors de l\'envoi du rappel pour le ticket {ticket.ticket_number}: {str(e)}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nRappels envoyés: {reminders_sent}'
            )
        )
