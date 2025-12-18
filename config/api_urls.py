from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tickets.api import RepairTicketViewSet, TicketEventViewSet
from assets.api import EquipmentViewSet
from accounts.api import ASCViewSet, UserViewSet

router = DefaultRouter()
router.register('tickets', RepairTicketViewSet, basename='ticket')
router.register('events', TicketEventViewSet, basename='event')
router.register('equipment', EquipmentViewSet, basename='equipment')
router.register('ascs', ASCViewSet, basename='asc')
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
