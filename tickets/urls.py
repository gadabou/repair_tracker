from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='list'),
    path('<int:pk>/', views.ticket_detail, name='detail'),
    path('create/', views.ticket_create, name='create'),
    path('<int:pk>/receive/', views.ticket_receive, name='receive'),
    path('<int:pk>/send/', views.ticket_send, name='send'),
    path('<int:pk>/mark-repaired/', views.ticket_mark_repaired, name='mark_repaired'),
    path('<int:pk>/comment/', views.ticket_add_comment, name='add_comment'),
    path('<int:pk>/cancel/', views.ticket_cancel, name='cancel'),
]
