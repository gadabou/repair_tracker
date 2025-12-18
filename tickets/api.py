from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RepairTicket, TicketEvent, Issue


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'issue_type', 'description', 'created_at']


class TicketEventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = TicketEvent
        fields = ['id', 'event_type', 'from_role', 'to_role', 'user', 'user_name', 'timestamp', 'comment']


class RepairTicketSerializer(serializers.ModelSerializer):
    equipment_name = serializers.StringRelatedField(source='equipment', read_only=True)
    asc_name = serializers.CharField(source='asc.get_full_name', read_only=True)
    delay_days = serializers.IntegerField(source='get_delay_days', read_only=True)
    delay_color = serializers.CharField(source='get_delay_color', read_only=True)
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = RepairTicket
        fields = [
            'id', 'ticket_number', 'equipment', 'equipment_name', 'asc', 'asc_name',
            'status', 'priority', 'current_stage', 'current_holder', 'created_at',
            'initial_send_date', 'repair_completed_date', 'closed_date',
            'initial_problem_description', 'resolution_notes', 'delay_days',
            'delay_color', 'issues'
        ]
        read_only_fields = ['ticket_number', 'created_at']


class RepairTicketViewSet(viewsets.ModelViewSet):
    queryset = RepairTicket.objects.all().select_related('equipment', 'asc', 'current_holder')
    serializer_class = RepairTicketSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        stage = self.request.query_params.get('stage')

        if status:
            queryset = queryset.filter(status=status)
        if stage:
            queryset = queryset.filter(current_stage=stage)

        return queryset

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Tickets en retard (> 14 jours)"""
        all_tickets = self.get_queryset().exclude(status='CLOSED')
        overdue_tickets = [t for t in all_tickets if t.get_delay_days() > 14]

        serializer = self.get_serializer(overdue_tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def warning(self, request):
        """Tickets en alerte (7-14 jours)"""
        all_tickets = self.get_queryset().exclude(status='CLOSED')
        warning_tickets = [t for t in all_tickets if 7 < t.get_delay_days() <= 14]

        serializer = self.get_serializer(warning_tickets, many=True)
        return Response(serializer.data)


class TicketEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TicketEvent.objects.all().select_related('ticket', 'user')
    serializer_class = TicketEventSerializer
