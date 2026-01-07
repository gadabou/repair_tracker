from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ASC, Supervisor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'phone', 'site')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'phone', 'site')}),
    )


@admin.register(ASC)
class ASCAdmin(admin.ModelAdmin):
    list_display = ['code', 'first_name', 'last_name', 'phone', 'site', 'supervisor', 'is_active']
    list_filter = [
        'is_active',
        'site__district__region',
        'site__district',
        'site'
    ]
    search_fields = ['code', 'first_name', 'last_name', 'phone', 'email']
    ordering = ['last_name', 'first_name']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identité', {
            'fields': ('first_name', 'last_name', 'code', 'gender', 'phone', 'email')
        }),
        ('Localisation', {
            'fields': ('site', 'zone_asc', 'supervisor')
        }),
        ('Statut', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ['code', 'first_name', 'last_name', 'email', 'phone', 'user', 'get_district', 'get_sites_count']
    list_filter = ['sites__district__region', 'sites__district']
    search_fields = ['code', 'first_name', 'last_name', 'email', 'phone', 'user__username', 'user__email']
    ordering = ['last_name', 'first_name']
    date_hierarchy = 'created_at'
    filter_horizontal = ['sites']

    fieldsets = (
        ('Compte Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations Personnelles', {
            'fields': ('first_name', 'last_name', 'code', 'email', 'phone')
        }),
        ('Sites Gérés', {
            'fields': ('sites',),
            'description': 'Tous les sites doivent appartenir au même district.'
        }),
    )

    def get_district(self, obj):
        """Display the district of managed sites"""
        return obj.district.name if obj.district else '-'
    get_district.short_description = 'District'
    get_district.admin_order_field = 'sites__district'

    def get_sites_count(self, obj):
        """Display the number of managed sites"""
        return obj.sites.count()
    get_sites_count.short_description = 'Sites Count'
