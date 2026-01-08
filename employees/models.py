from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Department(models.Model):
    """
    Équipe - Department/Team
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de l'équipe")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class SubDepartment(models.Model):
    """
    Sous-département - Sub-team within a Department
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='subdepartments',
        verbose_name="Équipe parent"
    )
    name = models.CharField(max_length=100, verbose_name="Nom du sous-département")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Sous-département"
        verbose_name_plural = "Sous-départements"
        ordering = ['department__name', 'name']
        unique_together = [['department', 'name']]

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Employee(models.Model):
    """
    Employé - Employee linked to a subdepartment (and thus to a department)
    """
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    subdepartment = models.ForeignKey(
        SubDepartment,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name="Sous-département"
    )
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="Matricule")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Genre")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    position = models.CharField(max_length=100, verbose_name="Poste")
    hire_date = models.DateField(verbose_name="Date d'embauche")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def department(self):
        """Auto-link to parent department via subdepartment"""
        return self.subdepartment.department


class EmployeeHistory(models.Model):
    """
    Historique des changements d'employés
    """
    ACTION_CHOICES = [
        ('CREATED', 'Créé'),
        ('UPDATED', 'Modifié'),
        ('DEACTIVATED', 'Désactivé'),
        ('REACTIVATED', 'Réactivé'),
        ('TRANSFERRED', 'Transféré'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Employé"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    old_subdepartment = models.ForeignKey(
        SubDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_old',
        verbose_name="Ancien sous-département"
    )
    new_subdepartment = models.ForeignKey(
        SubDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_new',
        verbose_name="Nouveau sous-département"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Utilisateur"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date et heure")

    class Meta:
        verbose_name = "Historique employé"
        verbose_name_plural = "Historiques employés"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_action_display()} - {self.timestamp}"
