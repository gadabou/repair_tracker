from django.contrib import admin
from .models import Department, SubDepartment, Employee, EmployeeHistory


class SubDepartmentInline(admin.TabularInline):
    model = SubDepartment
    extra = 1
    fields = ['name', 'code', 'is_active']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    inlines = [SubDepartmentInline]

    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'code', 'description')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )


@admin.register(SubDepartment)
class SubDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'code', 'description', 'department__name']
    ordering = ['department__name', 'name']

    fieldsets = (
        ('Informations principales', {
            'fields': ('department', 'name', 'code', 'description')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )


class EmployeeHistoryInline(admin.TabularInline):
    model = EmployeeHistory
    extra = 0
    readonly_fields = ['action', 'old_subdepartment', 'new_subdepartment', 'notes', 'user', 'timestamp']
    can_delete = False


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'last_name', 'first_name', 'subdepartment', 'position', 'is_active', 'hire_date']
    list_filter = ['is_active', 'gender', 'subdepartment__department', 'subdepartment', 'hire_date']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone', 'position']
    ordering = ['last_name', 'first_name']
    inlines = [EmployeeHistoryInline]

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'employee_id', 'gender', 'phone', 'email')
        }),
        ('Affectation', {
            'fields': ('subdepartment', 'position')
        }),
        ('Dates', {
            'fields': ('hire_date', 'end_date')
        }),
        ('Statut et Notes', {
            'fields': ('is_active', 'notes')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('subdepartment', 'subdepartment__department')


@admin.register(EmployeeHistory)
class EmployeeHistoryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'action', 'timestamp', 'user']
    list_filter = ['action', 'timestamp']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id', 'notes']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']

    fieldsets = (
        ('Information', {
            'fields': ('employee', 'action', 'user', 'timestamp')
        }),
        ('Détails', {
            'fields': ('old_subdepartment', 'new_subdepartment', 'notes')
        }),
    )
