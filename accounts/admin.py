from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ASC


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'phone', 'formation_sanitaire')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'phone', 'formation_sanitaire')}),
    )


@admin.register(ASC)
class ASCAdmin(admin.ModelAdmin):
    list_display = ['code', 'first_name', 'last_name', 'phone', 'formation_sanitaire', 'supervisor', 'is_active']
    list_filter = [
        'is_active',
        'formation_sanitaire__commune__district__region',
        'formation_sanitaire__commune__district',
        'formation_sanitaire'
    ]
    search_fields = ['code', 'first_name', 'last_name', 'phone', 'email']
    ordering = ['last_name', 'first_name']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identité', {
            'fields': ('first_name', 'last_name', 'code', 'gender', 'phone', 'email')
        }),
        ('Localisation', {
            'fields': ('formation_sanitaire', 'zone_asc', 'supervisor')
        }),
        ('Statut', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
