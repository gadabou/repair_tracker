from django.db import models
from accounts.models import ASC


class Equipment(models.Model):
    """Équipement (téléphone, tablette, etc.)"""
    TYPE_CHOICES = [
        ('PHONE', 'Téléphone'),
        ('TABLET', 'Tablette'),
        ('OTHER', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('FUNCTIONAL', 'Fonctionnel'),
        ('FAULTY', 'En panne')
    ]

    # Type et identification
    equipment_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type d'équipement"
    )
    brand = models.CharField(max_length=50, verbose_name="Marque")
    model = models.CharField(max_length=100, verbose_name="Modèle")
    imei = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="IMEI / Numéro de série"
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Numéro de série (additionnel)"
    )

    # Propriétaire
    owner = models.ForeignKey(
        ASC,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipments',
        verbose_name="Propriétaire ASC"
    )

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='FUNCTIONAL',
        verbose_name="État"
    )

    # Dates d'acquisition
    acquisition_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'acquisition"
    )
    warranty_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration de la garantie"
    )

    # Attribution à l'ASC
    assignment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'attribution à l'ASC"
    )
    reception_form = models.FileField(
        upload_to='reception_forms/',
        null=True,
        blank=True,
        verbose_name="Fiche de réception"
    )

    # Informations complémentaires
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
        ordering = ['-created_at']

    def __str__(self):
        owner_info = f" - {self.owner.get_full_name()}" if self.owner else ""
        return f"{self.brand} {self.model} ({self.imei}){owner_info}"

    def get_status_color(self):
        """Retourne la couleur Bootstrap pour le statut"""
        colors = {
            'FUNCTIONAL': 'success',
            'FAULTY': 'warning',
            'UNDER_REPAIR': 'info',
            'RETIRED': 'secondary',
        }
        return colors.get(self.status, 'secondary')


class EquipmentHistory(models.Model):
    """Historique des changements d'équipement"""
    ACTION_CHOICES = [
        ('CREATED', 'Créé'),
        ('ASSIGNED', 'Assigné'),
        ('STATUS_CHANGED', 'Statut modifié'),
        ('TRANSFERRED', 'Transféré'),
        ('RETIRED', 'Réformé'),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Équipement"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    old_value = models.CharField(max_length=255, blank=True, verbose_name="Ancienne valeur")
    new_value = models.CharField(max_length=255, blank=True, verbose_name="Nouvelle valeur")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Créé par"
    )

    class Meta:
        verbose_name = "Historique d'équipement"
        verbose_name_plural = "Historiques d'équipements"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.equipment.imei} - {self.get_action_display()} - {self.created_at:%d/%m/%Y}"
