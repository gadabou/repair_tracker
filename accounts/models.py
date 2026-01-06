from django.db import models
from django.contrib.auth.models import AbstractUser
from locations.models import FormationSanitaire, ZoneASC


class User(AbstractUser):
    """Utilisateur personnalisé avec rôles"""
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('SUPERVISOR', 'Superviseur'),
        ('PROGRAM', 'Programme'),
        ('LOGISTICS', 'Logistique'),
        ('ESANTE', 'E-Santé'),
        ('REPAIRER', 'Réparateur'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Rôle")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    formation_sanitaire = models.ForeignKey(
        FormationSanitaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Formation Sanitaire"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_supervisor(self):
        return self.role == 'SUPERVISOR'

    def is_program(self):
        return self.role == 'PROGRAM'

    def is_logistics(self):
        return self.role == 'LOGISTICS'

    def is_esante(self):
        return self.role == 'ESANTE'

    def is_repairer(self):
        return self.role == 'REPAIRER'

    def is_admin_role(self):
        return self.role == 'ADMIN'

    @classmethod
    def get_role_for_stage(cls, stage):
        """Retourne le rôle correspondant à une étape du workflow"""
        stage_to_role = {
            'SUPERVISOR': 'SUPERVISOR',
            'PROGRAM': 'PROGRAM',
            'LOGISTICS': 'LOGISTICS',
            'REPAIRER': 'REPAIRER',
            'ESANTE': 'ESANTE',
            'RETURNING_LOGISTICS': 'LOGISTICS',
            'RETURNING_PROGRAM': 'PROGRAM',
            'RETURNING_SUPERVISOR': 'SUPERVISOR',
        }
        return stage_to_role.get(stage)


class ASC(models.Model):
    """Agent de Santé Communautaire"""
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    # Identité
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code ASC")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Genre")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")

    # Localisation
    formation_sanitaire = models.ForeignKey(
        FormationSanitaire,
        on_delete=models.CASCADE,
        related_name='ascs',
        verbose_name="Formation Sanitaire"
    )
    zone_asc = models.ForeignKey(
        ZoneASC,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ascs',
        verbose_name="Zone ASC"
    )

    # Superviseur
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supervised_ascs',
        limit_choices_to={'role': 'SUPERVISOR'},
        verbose_name="Superviseur"
    )

    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    start_date = models.DateField(null=True, blank=True, verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")

    # Métadonnées
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ASC"
        verbose_name_plural = "ASCs"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.code} {self.formation_sanitaire})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def commune(self):
        return self.formation_sanitaire.commune

    @property
    def district(self):
        return self.formation_sanitaire.district

    @property
    def region(self):
        return self.formation_sanitaire.region
