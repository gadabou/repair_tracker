from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, ASC
from assets.models import Equipment


class ProblemType(models.Model):
    """Type de problème pour les tickets de réparation"""
    CATEGORY_CHOICES = [
        ('HARDWARE', 'Problèmes Matériels'),
        ('SOFTWARE', 'Problèmes Logiciels'),
        ('OTHER', 'Autre'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Nom du problème"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code unique",
        help_text="Code unique pour identifier le problème (ex: SCREEN_BROKEN)"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Catégorie"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Les problèmes sont affichés par ordre croissant"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Seuls les types actifs sont affichés dans le formulaire"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Type de problème"
        verbose_name_plural = "Types de problèmes"
        ordering = ['category', 'display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class RepairTicket(models.Model):
    """Ticket de réparation / acheminement"""
    STATUS_CHOICES = [
        ('OPEN', 'Ouvert'),
        ('IN_PROGRESS', 'En cours'),
        ('REPAIRED', 'Réparé'),
        ('RETURNING', 'Retour en cours'),
        ('CLOSED', 'Clôturé'),
        ('CANCELLED', 'Annulé'),
    ]

    STAGE_CHOICES = [
        ('SUPERVISOR', 'Superviseur'),
        ('PROGRAM', 'Programme'),
        ('LOGISTICS', 'Logistique'),
        ('REPAIRER', 'Réparateur'),
        ('ESANTE', 'E-Santé'),
        ('RETURNING_LOGISTICS', 'Retour - Logistique'),
        ('RETURNING_PROGRAM', 'Retour - Programme'),
        ('RETURNING_SUPERVISOR', 'Retour - Superviseur'),
        ('RETURNED_ASC', 'Retourné à l\'ASC'),
    ]

    # Identifiant unique
    ticket_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de ticket"
    )

    # Équipement et ASC
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='repair_tickets',
        verbose_name="Équipement"
    )
    asc = models.ForeignKey(
        ASC,
        on_delete=models.CASCADE,
        related_name='repair_tickets',
        verbose_name="ASC propriétaire"
    )

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN',
        verbose_name="Statut"
    )

    # Workflow tracking
    current_stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default='SUPERVISOR',
        verbose_name="Étape actuelle"
    )
    current_holder = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='held_tickets',
        verbose_name="Détenteur actuel"
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    initial_send_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'envoi initiale"
    )
    repair_completed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de fin de réparation"
    )
    closed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de clôture"
    )
    cancelled_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'annulation"
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Raison de l'annulation"
    )
    updated_at = models.DateTimeField(auto_now=True)

    # Créateur
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets',
        verbose_name="Créé par"
    )

    # Commentaires et notes
    initial_problem_description = models.TextField(
        verbose_name="Description du problème initial"
    )
    resolution_notes = models.TextField(
        blank=True,
        verbose_name="Notes de résolution"
    )

    class Meta:
        verbose_name = "Ticket de réparation"
        verbose_name_plural = "Tickets de réparation"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_number} - {self.equipment} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Génération automatique du numéro de ticket
            from django.utils.crypto import get_random_string
            timestamp = timezone.now().strftime('%Y%m%d')
            random_str = get_random_string(6, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            self.ticket_number = f"TKT-{timestamp}-{random_str}"
        super().save(*args, **kwargs)

    def get_delay_days(self):
        """Calcule le nombre de jours depuis l'envoi initial"""
        if self.closed_date:
            delta = self.closed_date - self.initial_send_date
        else:
            delta = timezone.now() - self.initial_send_date
        return delta.days

    def get_delay_color(self):
        """Retourne la couleur selon le délai (vert <= 7j, jaune <= 14j, rouge > 14j)"""
        days = self.get_delay_days()
        if days <= 7:
            return 'success'
        elif days <= 14:
            return 'warning'
        else:
            return 'danger'

    def get_delay_badge(self):
        """Retourne le badge HTML pour affichage"""
        days = self.get_delay_days()
        color = self.get_delay_color()
        return {'days': days, 'color': color}

    def get_current_stage_duration(self):
        """Calcule le temps passé à l'étape actuelle"""
        events = self.events.filter(
            event_type__in=['RECEIVED', 'SENT']
        ).order_by('-timestamp')

        if events.exists():
            last_event = events.first()
            delta = timezone.now() - last_event.timestamp
            return delta
        return timezone.now() - self.created_at

    def is_blocked(self):
        """Détermine si le ticket est bloqué (réception confirmée mais pas d'envoi)"""
        latest_event = self.events.order_by('-timestamp').first()
        if latest_event and latest_event.event_type == 'RECEIVED':
            # Vérifier s'il y a eu un envoi après cette réception
            sent_after = self.events.filter(
                event_type='SENT',
                timestamp__gt=latest_event.timestamp
            ).exists()
            return not sent_after
        return False

    def get_time_at_current_stage(self):
        """Calcule le nombre de jours passés à l'étape actuelle"""
        # Trouver le dernier événement RECEIVED ou SENT vers cette étape
        last_arrival = self.events.filter(
            to_role=self.current_stage
        ).order_by('-timestamp').first()

        if last_arrival:
            from django.utils import timezone
            delta = timezone.now() - last_arrival.timestamp
            return delta.days
        return 0

    def get_stage_status_color(self):
        """Retourne la couleur selon le temps passé à l'étape actuelle"""
        days = self.get_time_at_current_stage()
        if days >= 14:
            return 'danger'  # Rouge
        elif days >= 7:
            return 'warning'  # Jaune
        else:
            return 'success'  # Vert

    def get_time_by_stage(self):
        """Calcule le temps passé à chaque étape du workflow"""
        from collections import defaultdict
        stage_times = defaultdict(int)

        events = self.events.filter(
            event_type__in=['SENT', 'RECEIVED']
        ).order_by('timestamp')

        current_stage = None
        entry_time = None

        for event in events:
            if event.event_type == 'SENT':
                # Quitter une étape
                if current_stage and entry_time:
                    delta = event.timestamp - entry_time
                    stage_times[current_stage] += delta.days
                # Entrer dans une nouvelle étape
                current_stage = event.to_role
                entry_time = event.timestamp
            elif event.event_type == 'RECEIVED':
                # Confirmer l'entrée dans l'étape
                if event.to_role == current_stage:
                    entry_time = event.timestamp

        # Ajouter le temps de l'étape actuelle
        if current_stage and entry_time:
            from django.utils import timezone
            delta = timezone.now() - entry_time
            stage_times[current_stage] += delta.days

        return dict(stage_times)

    def should_send_reminder(self):
        """Vérifie si un rappel doit être envoyé"""
        days = self.get_time_at_current_stage()
        # Envoyer rappel à 7 jours et 14 jours
        return days == 7 or days == 14


class Issue(models.Model):
    """Problème signalé sur un ticket"""
    ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.CASCADE,
        related_name='issues',
        verbose_name="Ticket"
    )
    problem_type = models.ForeignKey(
        ProblemType,
        on_delete=models.PROTECT,
        related_name='issues',
        verbose_name="Type de problème"
    )
    description = models.TextField(blank=True, verbose_name="Description additionnelle")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Problème"
        verbose_name_plural = "Problèmes"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.problem_type.name} - {self.ticket.ticket_number}"


class TicketEvent(models.Model):
    """Événement dans le workflow d'un ticket"""
    EVENT_TYPE_CHOICES = [
        ('CREATED', 'Créé'),
        ('SENT', 'Envoyé'),
        ('RECEIVED', 'Reçu'),
        ('REPAIRED', 'Réparé'),
        ('RETURNED', 'Retourné'),
        ('CLOSED', 'Clôturé'),
        ('CANCELLED', 'Annulé'),
        ('COMMENT', 'Commentaire'),
    ]

    ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Ticket"
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name="Type d'événement"
    )

    # Source et destination
    from_role = models.CharField(
        max_length=30,
        choices=RepairTicket.STAGE_CHOICES,
        blank=True,
        verbose_name="De"
    )
    to_role = models.CharField(
        max_length=30,
        choices=RepairTicket.STAGE_CHOICES,
        blank=True,
        verbose_name="Vers"
    )

    # Utilisateur et timestamp
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Utilisateur"
    )
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Date/Heure")

    # Détails
    comment = models.TextField(blank=True, verbose_name="Commentaire")
    attachment = models.FileField(
        upload_to='ticket_attachments/',
        blank=True,
        null=True,
        verbose_name="Pièce jointe"
    )

    class Meta:
        verbose_name = "Événement de ticket"
        verbose_name_plural = "Événements de tickets"
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.get_event_type_display()} - {self.timestamp:%d/%m/%Y %H:%M}"


class TicketComment(models.Model):
    """Commentaire sur un ticket"""
    ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Ticket"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Utilisateur"
    )
    comment = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['created_at']

    def __str__(self):
        return f"Commentaire sur {self.ticket.ticket_number} par {self.user}"


class DelayAlertRecipient(models.Model):
    """Destinataire des alertes de dépassement de délai"""
    RECIPIENT_TYPE_CHOICES = [
        ('PRIMARY', 'Destinataire principal (reçoit en copie)'),
        ('DEPARTMENT', 'Membre de département (reçoit selon le département)'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Email pour les notifications (modifiable)"
    )
    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_TYPE_CHOICES,
        default='PRIMARY',
        verbose_name="Type de destinataire",
        help_text="Principal = toujours en copie, Département = selon département concerné"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Recevoir les notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Destinataire d'alerte"
        verbose_name_plural = "Destinataires d'alertes"
        ordering = ['user__last_name', 'user__first_name']
        unique_together = ['user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.email}"

    def save(self, *args, **kwargs):
        # Si l'email n'est pas défini, utiliser celui de l'utilisateur
        if not self.email and self.user.email:
            self.email = self.user.email
        super().save(*args, **kwargs)


class DelayAlertLog(models.Model):
    """Journal des alertes envoyées"""
    ticket = models.ForeignKey(
        RepairTicket,
        on_delete=models.CASCADE,
        related_name='delay_alerts',
        verbose_name="Ticket"
    )
    stage = models.CharField(
        max_length=30,
        choices=RepairTicket.STAGE_CHOICES,
        verbose_name="Étape concernée"
    )
    days_in_stage = models.IntegerField(
        verbose_name="Jours dans l'étape"
    )
    recipients = models.TextField(
        verbose_name="Destinataires",
        help_text="Liste des emails séparés par des virgules"
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Envoyé le")
    email_sent_successfully = models.BooleanField(
        default=False,
        verbose_name="Email envoyé avec succès"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Message d'erreur"
    )

    class Meta:
        verbose_name = "Journal d'alerte"
        verbose_name_plural = "Journaux d'alertes"
        ordering = ['-sent_at']

    def __str__(self):
        return f"Alerte {self.ticket.ticket_number} - {self.stage} - {self.days_in_stage} jours"
