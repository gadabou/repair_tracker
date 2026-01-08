from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, SubDepartment, Employee, EmployeeHistory


# ========== DEPARTMENT VIEWS ==========

@login_required
def department_list(request):
    """Liste des équipes (départements)"""
    departments = Department.objects.all().prefetch_related('subdepartments')
    context = {'departments': departments}
    return render(request, 'employees/department_list.html', context)


@login_required
def department_detail(request, pk):
    """Détail d'une équipe (département)"""
    department = get_object_or_404(
        Department.objects.prefetch_related('subdepartments', 'subdepartments__employees'),
        pk=pk
    )
    context = {'department': department}
    return render(request, 'employees/department_detail.html', context)


# ========== SUBDEPARTMENT VIEWS ==========

@login_required
def subdepartment_detail(request, pk):
    """Détail d'un sous-département"""
    subdepartment = get_object_or_404(
        SubDepartment.objects.select_related('department').prefetch_related('employees'),
        pk=pk
    )
    context = {'subdepartment': subdepartment}
    return render(request, 'employees/subdepartment_detail.html', context)


# ========== EMPLOYEE VIEWS ==========

@login_required
def employee_list(request):
    """Liste des employés"""
    employees = Employee.objects.all().select_related(
        'subdepartment', 'subdepartment__department'
    ).prefetch_related('equipments')

    # Filtres
    is_active = request.GET.get('is_active')
    subdepartment_id = request.GET.get('subdepartment')
    department_id = request.GET.get('department')

    if is_active:
        employees = employees.filter(is_active=(is_active == 'true'))
    if subdepartment_id:
        employees = employees.filter(subdepartment_id=subdepartment_id)
    if department_id:
        employees = employees.filter(subdepartment__department_id=department_id)

    departments = Department.objects.filter(is_active=True)
    subdepartments = SubDepartment.objects.filter(is_active=True).select_related('department')

    context = {
        'employees': employees,
        'departments': departments,
        'subdepartments': subdepartments,
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    """Détail d'un employé"""
    employee = get_object_or_404(
        Employee.objects.select_related('subdepartment', 'subdepartment__department'),
        pk=pk
    )
    history = employee.history.all().select_related('user', 'old_subdepartment', 'new_subdepartment')
    equipments = employee.equipments.all()

    context = {
        'employee': employee,
        'history': history,
        'equipments': equipments,
    }
    return render(request, 'employees/employee_detail.html', context)


@login_required
def employee_create(request):
    """Créer un employé"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        employee_id = request.POST.get('employee_id')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subdepartment_id = request.POST.get('subdepartment')
        position = request.POST.get('position')
        hire_date = request.POST.get('hire_date')
        end_date = request.POST.get('end_date')
        notes = request.POST.get('notes')

        # Vérifier que le matricule n'existe pas déjà
        if Employee.objects.filter(employee_id=employee_id).exists():
            messages.error(request, f'Un employé avec le matricule "{employee_id}" existe déjà.')
            subdepartments = SubDepartment.objects.filter(is_active=True).select_related('department')
            context = {
                'subdepartments': subdepartments,
                'gender_choices': Employee.GENDER_CHOICES,
            }
            return render(request, 'employees/employee_create.html', context)

        # Récupérer le sous-département
        subdepartment = get_object_or_404(SubDepartment, pk=subdepartment_id)

        # Créer l'employé
        employee = Employee.objects.create(
            first_name=first_name,
            last_name=last_name,
            employee_id=employee_id,
            gender=gender,
            phone=phone,
            email=email,
            subdepartment=subdepartment,
            position=position,
            hire_date=hire_date,
            end_date=end_date if end_date else None,
            notes=notes
        )

        # Créer un enregistrement d'historique
        EmployeeHistory.objects.create(
            employee=employee,
            action='CREATED',
            new_subdepartment=subdepartment,
            notes=f'Employé créé dans {subdepartment}',
            user=request.user
        )

        messages.success(request, f'Employé {employee.get_full_name()} créé avec succès!')
        return redirect('employees:employee_detail', pk=employee.pk)

    # GET - Afficher le formulaire
    subdepartments = SubDepartment.objects.filter(is_active=True).select_related('department')
    context = {
        'subdepartments': subdepartments,
        'gender_choices': Employee.GENDER_CHOICES,
    }
    return render(request, 'employees/employee_create.html', context)


@login_required
def employee_update(request, pk):
    """Modifier un employé"""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        old_subdepartment = employee.subdepartment

        # Récupérer les données du formulaire
        employee.first_name = request.POST.get('first_name')
        employee.last_name = request.POST.get('last_name')
        employee.gender = request.POST.get('gender')
        employee.phone = request.POST.get('phone')
        employee.email = request.POST.get('email')
        employee.position = request.POST.get('position')
        employee.hire_date = request.POST.get('hire_date')
        end_date = request.POST.get('end_date')
        employee.end_date = end_date if end_date else None
        employee.notes = request.POST.get('notes')

        # Vérifier si le sous-département a changé
        new_subdepartment_id = request.POST.get('subdepartment')
        new_subdepartment = get_object_or_404(SubDepartment, pk=new_subdepartment_id)

        if old_subdepartment != new_subdepartment:
            employee.subdepartment = new_subdepartment
            # Créer un historique de transfert
            EmployeeHistory.objects.create(
                employee=employee,
                action='TRANSFERRED',
                old_subdepartment=old_subdepartment,
                new_subdepartment=new_subdepartment,
                notes=f'Transféré de {old_subdepartment} vers {new_subdepartment}',
                user=request.user
            )
        else:
            # Créer un historique de modification
            EmployeeHistory.objects.create(
                employee=employee,
                action='UPDATED',
                new_subdepartment=new_subdepartment,
                notes='Informations mises à jour',
                user=request.user
            )

        employee.save()
        messages.success(request, f'Employé {employee.get_full_name()} modifié avec succès!')
        return redirect('employees:employee_detail', pk=employee.pk)

    # GET - Afficher le formulaire
    subdepartments = SubDepartment.objects.filter(is_active=True).select_related('department')
    context = {
        'employee': employee,
        'subdepartments': subdepartments,
        'gender_choices': Employee.GENDER_CHOICES,
    }
    return render(request, 'employees/employee_update.html', context)


@login_required
def employee_toggle_active(request, pk):
    """Activer/désactiver un employé"""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        old_status = employee.is_active
        employee.is_active = not employee.is_active
        employee.save()

        # Créer un historique
        action = 'REACTIVATED' if employee.is_active else 'DEACTIVATED'
        EmployeeHistory.objects.create(
            employee=employee,
            action=action,
            new_subdepartment=employee.subdepartment,
            notes=f'Employé {"réactivé" if employee.is_active else "désactivé"}',
            user=request.user
        )

        status_text = 'activé' if employee.is_active else 'désactivé'
        messages.success(request, f'Employé {employee.get_full_name()} {status_text} avec succès!')

    return redirect('employees:employee_detail', pk=employee.pk)
