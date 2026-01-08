"""
Module pour l'envoi de notifications par email lors des transitions de tickets
"""
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.models import User


def get_team_members_by_role(role):
    """
    Récupère tous les membres d'une équipe selon leur rôle
    """
    role_mapping = {
        'SUPERVISOR': 'SUPERVISOR',
        'PROGRAM': 'PROGRAM',
        'LOGISTICS': 'LOGISTICS',
        'REPAIRER': 'REPAIRER',
        'ESANTE': 'ESANTE',
        'RETURNING_LOGISTICS': 'LOGISTICS',
        'RETURNING_PROGRAM': 'PROGRAM',
        'RETURNING_SUPERVISOR': 'SUPERVISOR',
    }

    target_role = role_mapping.get(role, role)
    users = User.objects.filter(role=target_role, is_active=True, email__isnull=False).exclude(email='')

    # Log des membres trouvés
    if users.exists():
        print(f"  Membres trouvés pour le rôle {target_role}:")
        for user in users:
            print(f"    - {user.get_full_name()} ({user.email})")
    else:
        print(f"  ⚠️ Aucun membre trouvé pour le rôle {target_role}")

    return users


def send_ticket_notification(ticket, recipient, sender, to_role, comment=''):
    """
    Envoie une notification par email lors de l'envoi d'un ticket

    Args:
        ticket: Le ticket concerné
        recipient: L'utilisateur destinataire principal (peut être None)
        sender: L'utilisateur qui envoie le ticket
        to_role: Le rôle/département destinataire
        comment: Commentaire optionnel
    """
    print("\n" + "="*80)
    print("DÉBUT DE L'ENVOI D'EMAIL DE NOTIFICATION")
    print("="*80)
    print(f"Ticket: {ticket.ticket_number}")
    print(f"Destinataire principal: {recipient.get_full_name() if recipient else 'Aucun'}")
    print(f"Expéditeur: {sender.get_full_name()}")
    print(f"Rôle destinataire: {to_role}")
    print(f"Commentaire: {comment if comment else 'Aucun'}")

    try:
        # Récupérer tous les membres de l'équipe destinataire
        print(f"\nRecherche des membres de l'équipe pour le rôle: {to_role}")
        team_members = get_team_members_by_role(to_role)
        print(f"Nombre de membres trouvés: {team_members.count()}")

        # Préparer les emails
        recipient_emails = []
        cc_emails = []

        # Si un destinataire spécifique est défini
        if recipient and recipient.email:
            recipient_emails.append(recipient.email)
            # Les autres membres de l'équipe en copie
            cc_emails = [user.email for user in team_members if user.id != recipient.id and user.email]
            print(f"\nDestinataire spécifique défini: {recipient.email}")
            print(f"Emails en copie: {', '.join(cc_emails) if cc_emails else 'Aucun'}")
        else:
            # Sinon, envoyer à tous les membres de l'équipe
            recipient_emails = [user.email for user in team_members if user.email]
            print(f"\nAucun destinataire spécifique, envoi à toute l'équipe")
            print(f"Destinataires: {', '.join(recipient_emails) if recipient_emails else 'Aucun'}")

        if not recipient_emails:
            print(f"\n⚠️ ERREUR: Aucun destinataire email trouvé pour le rôle {to_role}")
            print("="*80 + "\n")
            return False

        print(f"\n✓ Total destinataires principaux: {len(recipient_emails)}")
        print(f"✓ Total destinataires en copie: {len(cc_emails)}")

        # Préparer le contexte pour le template
        context = {
            'ticket': ticket,
            'recipient': recipient,
            'sender': sender,
            'to_role': to_role,
            'to_role_display': dict(ticket.STAGE_CHOICES).get(to_role, to_role),
            'comment': comment,
            'ticket_url': f"{settings.SITE_URL}/tickets/{ticket.pk}/receive/?auto_confirm=1" if hasattr(settings, 'SITE_URL') else f"http://localhost:8000/tickets/{ticket.pk}/receive/?auto_confirm=1",
        }

        # Préparer le sujet
        subject = f"[IH Equipment Manager] Nouveau ticket à traiter - {ticket.ticket_number}"
        print(f"\nSujet de l'email: {subject}")

        # Préparer le message HTML
        print("\nGénération du message HTML depuis le template...")
        html_message = render_to_string('tickets/emails/ticket_notification.html', context)
        plain_message = strip_tags(html_message)
        print("✓ Message HTML généré avec succès")

        # Afficher la configuration email
        print("\n" + "-"*80)
        print("CONFIGURATION EMAIL")
        print("-"*80)
        print(f"Backend email: {settings.EMAIL_BACKEND}")
        print(f"Hôte SMTP: {settings.EMAIL_HOST}")
        print(f"Port SMTP: {settings.EMAIL_PORT}")
        print(f"Utilise TLS: {settings.EMAIL_USE_TLS}")
        print(f"Utilisateur SMTP: {settings.EMAIL_HOST_USER}")
        print(f"Expéditeur (from): {settings.EMAIL_HOST_USER}")
        print(f"URL du site: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}")
        print("-"*80)

        # Créer l'email
        print("\nCréation de l'objet EmailMessage...")
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_emails,
            cc=cc_emails,
        )
        email.content_subtype = 'html'  # Le contenu principal est en HTML
        print("✓ Objet EmailMessage créé")

        # Envoyer l'email
        print("\n📧 ENVOI DE L'EMAIL EN COURS...")
        email.send(fail_silently=False)
        print("✓ Email envoyé avec succès!")

        print(f"\n{'='*80}")
        print(f"✅ EMAIL ENVOYÉ AVEC SUCCÈS")
        print(f"{'='*80}")
        print(f"✓ {len(recipient_emails)} destinataire(s) principal(aux)")
        print(f"✓ {len(cc_emails)} destinataire(s) en copie")
        print(f"{'='*80}\n")
        return True

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ ERREUR LORS DE L'ENVOI DE L'EMAIL")
        print(f"{'='*80}")
        print(f"Type d'erreur: {type(e).__name__}")
        print(f"Message d'erreur: {str(e)}")
        import traceback
        print(f"\nTrace complète:")
        print(traceback.format_exc())
        print(f"{'='*80}\n")
        return False
