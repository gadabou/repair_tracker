from rest_framework import viewsets, serializers
from .models import ASC, User


class ASCSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    formation_sanitaire_name = serializers.StringRelatedField(source='formation_sanitaire', read_only=True)

    class Meta:
        model = ASC
        fields = [
            'id', 'first_name', 'last_name', 'code', 'gender', 'phone', 'email',
            'formation_sanitaire', 'formation_sanitaire_name', 'zone_asc',
            'supervisor', 'supervisor_name', 'is_active', 'start_date',
            'end_date', 'created_at'
        ]


class ASCViewSet(viewsets.ModelViewSet):
    queryset = ASC.objects.all().select_related('formation_sanitaire', 'supervisor', 'zone_asc')
    serializer_class = ASCSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                code__icontains=search
            )

        return queryset


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'role_display', 'phone']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')

        if role:
            queryset = queryset.filter(role=role)

        return queryset
