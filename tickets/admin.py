from django.contrib import admin
from .models import RepairTicket, Issue, TicketEvent, TicketComment


class IssueInline(admin.TabularInline):
    model = Issue
    extra = 1


class TicketEventInline(admin.TabularInline):
    model = TicketEvent
    extra = 0
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


class TicketCommentInline(admin.StackedInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(RepairTicket)
class RepairTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'equipment', 'asc', 'status', 'current_stage', 'priority', 'get_delay_days', 'created_at']
    list_filter = ['status', 'priority', 'current_stage', 'created_at']
    search_fields = ['ticket_number', 'equipment__imei', 'asc__first_name', 'asc__last_name']
    ordering = ['-created_at']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at', 'get_delay_days']
    date_hierarchy = 'created_at'
    inlines = [IssueInline, TicketEventInline, TicketCommentInline]

    fieldsets = (
        ('Informations du ticket', {
            'fields': ('ticket_number', 'equipment', 'asc', 'created_by')
        }),
        ('Statut et Priorité', {
            'fields': ('status', 'priority', 'current_stage', 'current_holder')
        }),
        ('Dates', {
            'fields': ('initial_send_date', 'repair_completed_date', 'closed_date', 'created_at', 'updated_at')
        }),
        ('Descriptions', {
            'fields': ('initial_problem_description', 'resolution_notes')
        }),
    )

    def get_delay_days(self, obj):
        return f"{obj.get_delay_days()} jours"
    get_delay_days.short_description = "Délai"


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'issue_type', 'created_at']
    list_filter = ['issue_type', 'created_at']
    search_fields = ['ticket__ticket_number', 'description']
    ordering = ['-created_at']


@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'event_type', 'from_role', 'to_role', 'user', 'timestamp']
    list_filter = ['event_type', 'from_role', 'to_role', 'timestamp']
    search_fields = ['ticket__ticket_number', 'comment']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['ticket__ticket_number', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
