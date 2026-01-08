# -*- coding: utf-8 -*-
"""
Commande Django pour verifier les tickets qui depassent 14 jours dans une etape
et envoyer des alertes par email aux destinataires configures.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tickets.models import RepairTicket, DelayAlertRecipient, DelayAlertLog
from datetime import timedelta


class Command(BaseCommand):
    help = 'Vérifie les tickets qui dépassent 14 jours dans une étape et envoie des alertes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher les alertes sans envoyer d\'emails',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer l\'envoi même si une alerte a déjà été envoyée',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('=== Vérification des dépassements de délai ==='))
        self.stdout.write(f'Date/Heure: {timezone.now().strftime("%d/%m/%Y %H:%M")}')
        self.stdout.write(f'Mode: {"DRY RUN (aucun email ne sera envoyé)" if dry_run else "PRODUCTION"}')
        self.stdout.write('')

        # Récupérer les destinataires actifs
        recipients = DelayAlertRecipient.objects.filter(is_active=True).select_related('user')

        if not recipients.exists():
            self.stdout.write(self.style.WARNING('Aucun destinataire configuré. Veuillez configurer les destinataires dans l\'interface.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Destinataires configurés: {recipients.count()}'))
        for recipient in recipients:
            self.stdout.write(f'  - {recipient.user.get_full_name()} ({recipient.email})')
        self.stdout.write('')

        # Récupérer les tickets actifs (non clôturés, non annulés)
        active_tickets = RepairTicket.objects.filter(
            status__in=['OPEN', 'IN_PROGRESS', 'REPAIRED', 'RETURNING']
        ).select_related('equipment', 'asc', 'current_holder')

        self.stdout.write(f'Tickets actifs à vérifier: {active_tickets.count()}')
        self.stdout.write('')

        alerts_to_send = []

        for ticket in active_tickets:
            # Calculer le nombre de jours dans l'étape actuelle
            days_in_stage = ticket.get_time_at_current_stage()

            # Vérifier si le ticket dépasse 14 jours
            if days_in_stage >= 14:
                # Vérifier si une alerte a déjà été envoyée aujourd'hui pour cette étape
                # (on compare la date uniquement, pas l'heure, pour permettre un envoi quotidien)
                if not force:
                    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    recent_alert = DelayAlertLog.objects.filter(
                        ticket=ticket,
                        stage=ticket.current_stage,
                        sent_at__gte=today_start
                    ).exists()

                    if recent_alert:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⏭️  {ticket.ticket_number}: Alerte déjà envoyée aujourd\'hui (ignoré)'
                            )
                        )
                        continue

                alerts_to_send.append({
                    'ticket': ticket,
                    'days_in_stage': days_in_stage,
                    'stage': ticket.current_stage,
                    'stage_display': ticket.get_current_stage_display(),
                })

                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  {ticket.ticket_number}: {days_in_stage} jours à l\'étape "{ticket.get_current_stage_display()}"'
                    )
                )

        if not alerts_to_send:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ Aucun dépassement de délai détecté.'))
            return

        self.stdout.write('')
        self.stdout.write(self.style.WARNING(f'📧 {len(alerts_to_send)} alerte(s) à envoyer'))
        self.stdout.write('')

        if dry_run:
            self.stdout.write(self.style.WARNING('Mode DRY RUN - Aucun email ne sera envoyé'))
            for alert in alerts_to_send:
                self.stdout.write(f'  📧 {alert["ticket"].ticket_number}: {alert["days_in_stage"]} jours')
            return

        # Séparer les destinataires par type
        primary_recipients = recipients.filter(recipient_type='PRIMARY')
        department_recipients = recipients.filter(recipient_type='DEPARTMENT')

        success_count = 0
        error_count = 0

        for alert in alerts_to_send:
            ticket = alert['ticket']
            days = alert['days_in_stage']
            stage = alert['stage']
            stage_display = alert['stage_display']

            # Déterminer les destinataires principaux pour ce ticket
            # Ce sont les membres du département/rôle concerné par l'étape actuelle
            main_recipients = []
            cc_recipients = []

            # Trouver les utilisateurs du rôle correspondant à l'étape
            role_for_stage = User.get_role_for_stage(stage)
            if role_for_stage:
                # Récupérer les destinataires du département concerné qui ont ce rôle
                for dept_recipient in department_recipients:
                    if dept_recipient.user.role == role_for_stage:
                        main_recipients.append(dept_recipient.email)

            # Ajouter les destinataires principaux (toujours en copie)
            for primary_recipient in primary_recipients:
                cc_recipients.append(primary_recipient.email)

            # Si aucun destinataire principal spécifique, envoyer à tous
            if not main_recipients:
                main_recipients = [r.email for r in primary_recipients]
                cc_recipients = []

            all_recipients = list(set(main_recipients + cc_recipients))

            if not all_recipients:
                self.stdout.write(
                    self.style.WARNING(f'⏭️  {ticket.ticket_number}: Aucun destinataire trouvé (ignoré)')
                )
                continue

            # Préparer le contenu de l'email
            subject = f'⚠️ Alerte: Équipement bloqué {days} jours - {ticket.ticket_number}'

            # Contenu HTML personnalisé et amical
            html_message = self._generate_friendly_email_html(
                ticket, days, stage_display, role_for_stage
            )
            plain_message = strip_tags(html_message)

            try:
                # Envoyer l'email avec distinction destinataires/copie
                from django.core.mail import EmailMessage

                email = EmailMessage(
                    subject=subject,
                    body=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@repair-tracker.com',
                    to=main_recipients,
                    cc=cc_recipients,
                )
                email.content_subtype = "html"
                email.send(fail_silently=False)

                # Enregistrer dans le journal
                DelayAlertLog.objects.create(
                    ticket=ticket,
                    stage=stage,
                    days_in_stage=days,
                    recipients=f"TO: {', '.join(main_recipients)} | CC: {', '.join(cc_recipients)}",
                    email_sent_successfully=True
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Email envoyé pour {ticket.ticket_number} - '
                        f'TO: {len(main_recipients)}, CC: {len(cc_recipients)}'
                    )
                )
                success_count += 1

            except Exception as e:
                # Enregistrer l'erreur
                DelayAlertLog.objects.create(
                    ticket=ticket,
                    stage=stage,
                    days_in_stage=days,
                    recipients=f"TO: {', '.join(main_recipients)} | CC: {', '.join(cc_recipients)}",
                    email_sent_successfully=False,
                    error_message=str(e)
                )

                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur lors de l\'envoi pour {ticket.ticket_number}: {e}')
                )
                error_count += 1

        # Résumé
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Résumé ==='))
        self.stdout.write(f'Alertes envoyées avec succès: {success_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Erreurs: {error_count}'))
        self.stdout.write('')

    def _generate_friendly_email_html(self, ticket, days, stage_display, role):
        """Génère le contenu HTML amical de l'email d'alerte"""
        # Déterminer le ton en fonction du département
        department_greetings = {
            'PROGRAM': 'l\'équipe Programme',
            'LOGISTICS': 'l\'équipe Logistique',
            'REPAIRER': 'l\'équipe de réparation',
            'ESANTE': 'l\'équipe E-Santé',
            'SUPERVISOR': 'les superviseurs',
        }

        greeting = department_greetings.get(role, 'Cher(s) collègue(s)')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; }}
                .container {{ max-width: 650px; margin: 20px auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 300; }}
                .greeting {{ background-color: #f8f9fa; padding: 20px; border-left: 4px solid #667eea; margin: 20px; }}
                .greeting p {{ margin: 5px 0; font-size: 16px; }}
                .content {{ padding: 0 20px 20px 20px; }}
                .alert-box {{ background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center; }}
                .alert-box .days {{ font-size: 48px; font-weight: bold; color: #d63031; margin: 10px 0; }}
                .alert-box .message {{ font-size: 18px; color: #2d3436; }}
                .info-card {{ background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .info-row {{ display: flex; padding: 10px 0; border-bottom: 1px solid #e0e0e0; }}
                .info-row:last-child {{ border-bottom: none; }}
                .info-label {{ font-weight: 600; color: #667eea; width: 40%; }}
                .info-value {{ width: 60%; color: #2d3436; }}
                .problem-box {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                .action-box {{ background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 20px; margin: 20px 0; border-radius: 4px; }}
                .action-box h3 {{ margin-top: 0; color: #1976d2; }}
                .action-box ul {{ margin: 10px 0; padding-left: 20px; }}
                .action-box li {{ margin: 8px 0; }}
                .footer {{ background-color: #2d3436; color: #b2bec3; padding: 20px; text-align: center; font-size: 12px; }}
                .footer p {{ margin: 5px 0; }}
                .emoji {{ font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📱 Rappel Amical - Repair Tracker</h1>
                </div>

                <div class="greeting">
                    <p><strong>Bonjour {greeting},</strong></p>
                    <p>Nous espérons que vous allez bien. Nous vous contactons concernant un équipement qui nécessite votre attention.</p>
                </div>

                <div class="content">
                    <div class="alert-box">
                        <div class="message">L'équipement est dans votre département depuis</div>
                        <div class="days">{days} jours</div>
                        <div class="message">⏰ Délai recommandé dépassé (14 jours)</div>
                    </div>

                    <div class="info-card">
                        <h2 style="color: #667eea; margin-top: 0;">📋 Informations sur l'équipement</h2>

                        <div class="info-row">
                            <div class="info-label">Numéro de ticket</div>
                            <div class="info-value"><strong>{ticket.ticket_number}</strong></div>
                        </div>

                        <div class="info-row">
                            <div class="info-label">Équipement</div>
                            <div class="info-value">{ticket.equipment.model}<br><small>{ticket.equipment.serial_number}</small></div>
                        </div>

                        <div class="info-row">
                            <div class="info-label">ASC propriétaire</div>
                            <div class="info-value">{ticket.asc.get_full_name()}<br><small>Code: {ticket.asc.code}</small></div>
                        </div>

                        <div class="info-row">
                            <div class="info-label">Département actuel</div>
                            <div class="info-value"><strong>{stage_display}</strong></div>
                        </div>

                        <div class="info-row">
                            <div class="info-label">Détenteur actuel</div>
                            <div class="info-value">{ticket.current_holder.get_full_name() if ticket.current_holder else "Non défini"}</div>
                        </div>

                        <div class="info-row">
                            <div class="info-label">Date d'arrivée</div>
                            <div class="info-value">{ticket.created_at.strftime("%d/%m/%Y")}</div>
                        </div>
                    </div>

                    <div class="problem-box">
                        <strong>🔧 Problème signalé :</strong><br>
                        {ticket.initial_problem_description}
                    </div>

                    <div class="action-box">
                        <h3>💡 Que pouvez-vous faire ?</h3>
                        <ul>
                            <li>Vérifier l'état actuel de l'équipement dans votre département</li>
                            <li>Si la réparation/traitement est terminée, transférer l'équipement à l'étape suivante</li>
                            <li>Si vous rencontrez des difficultés, ajouter un commentaire sur le ticket</li>
                            <li>Contacter l'équipe support si besoin d'assistance</li>
                        </ul>
                        <p style="margin-bottom: 0;"><strong>Objectif :</strong> Réduire le délai total de traitement pour améliorer le service aux ASC 🎯</p>
                    </div>

                    <p style="text-align: center; color: #636e72; font-size: 14px; margin-top: 30px;">
                        <em>Nous comptons sur votre collaboration pour maintenir un flux efficace.<br>
                        Merci pour votre engagement ! 🙏</em>
                    </p>
                </div>

                <div class="footer">
                    <p><strong>Repair Tracker</strong> - Système de suivi des réparations d'équipements ASC</p>
                    <p>Cet email a été envoyé automatiquement. Pour toute question, contactez l'administrateur système.</p>
                    <p style="margin-top: 10px; font-size: 10px;">Email généré le {timezone.now().strftime("%d/%m/%Y à %H:%M")}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
