from rest_framework import viewsets, serializers
from .models import Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id', 'equipment_type', 'brand', 'model', 'imei', 'serial_number',
            'owner', 'owner_name', 'status', 'acquisition_date',
            'warranty_expiry_date', 'notes', 'created_at'
        ]


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().select_related('owner')
    serializer_class = EquipmentSerializer
    pagination_class = None  # Désactiver la pagination pour obtenir tous les résultats

    def get_queryset(self):
        queryset = super().get_queryset()
        asc_id = self.request.query_params.get('asc_id')

        if asc_id:
            queryset = queryset.filter(owner_id=asc_id)

        return queryset
