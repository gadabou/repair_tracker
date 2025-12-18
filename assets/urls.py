from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.equipment_list, name='list'),
    path('<int:pk>/', views.equipment_detail, name='detail'),
    path('<int:pk>/assign/', views.equipment_assign, name='assign'),
    path('create/', views.equipment_create, name='create'),
    path('asc/<int:asc_pk>/assign/', views.asc_assign_equipment, name='asc_assign_equipment'),
]
