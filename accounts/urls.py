from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('ascs/', views.asc_list, name='asc_list'),
    path('ascs/<int:pk>/', views.asc_detail, name='asc_detail'),
    path('ascs/create/', views.asc_create, name='asc_create'),
]
