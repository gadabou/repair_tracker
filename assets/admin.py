from django.contrib import admin
from .models import Equipment, EquipmentHistory


class EquipmentHistoryInline(admin.TabularInline):
    model = EquipmentHistory
    extra = 0
    readonly_fields = ['action', 'old_value', 'new_value', 'created_at', 'created_by']
    can_delete = False


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['imei', 'equipment_type', 'brand', 'model', 'owner', 'status', 'created_at']
    list_filter = ['equipment_type', 'status', 'brand']
    search_fields = ['imei', 'serial_number', 'brand', 'model', 'owner__first_name', 'owner__last_name']
    ordering = ['-created_at']
    inlines = [EquipmentHistoryInline]

    fieldsets = (
        ('Type et Identification', {
            'fields': ('equipment_type', 'brand', 'model', 'imei', 'serial_number')
        }),
        ('Propriétaire', {
            'fields': ('owner',)
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Dates', {
            'fields': ('acquisition_date', 'warranty_expiry_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(EquipmentHistory)
class EquipmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'action', 'created_at', 'created_by']
    list_filter = ['action', 'created_at']
    search_fields = ['equipment__imei', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
