from rest_framework import viewsets, serializers
from .models import ASC, User, Supervisor


class ASCSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    site_name = serializers.StringRelatedField(source='site', read_only=True)

    class Meta:
        model = ASC
        fields = [
            'id', 'first_name', 'last_name', 'code', 'gender', 'phone', 'email',
            'site', 'site_name', 'zone_asc',
            'supervisor', 'supervisor_name', 'is_active', 'start_date',
            'end_date', 'created_at'
        ]


class ASCViewSet(viewsets.ModelViewSet):
    queryset = ASC.objects.all().select_related('site', 'supervisor', 'zone_asc')
    serializer_class = ASCSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Si l'utilisateur est un superviseur, ne montrer que les ASCs de ses sites
        if user.is_authenticated and user.role == 'SUPERVISOR':
            try:
                supervisor = Supervisor.objects.get(user=user)
                # Récupérer les IDs des sites gérés par ce superviseur
                supervisor_site_ids = supervisor.sites.values_list('id', flat=True)
                # Filtrer les ASCs pour ne montrer que ceux de ces sites
                queryset = queryset.filter(site_id__in=supervisor_site_ids)
            except Supervisor.DoesNotExist:
                # Si le superviseur n'a pas de profil Supervisor, ne montrer aucun ASC
                queryset = queryset.none()

        # Recherche
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
