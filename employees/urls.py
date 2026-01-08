from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),

    # SubDepartment URLs
    path('subdepartments/<int:pk>/', views.subdepartment_detail, name='subdepartment_detail'),

    # Employee URLs
    path('', views.employee_list, name='employee_list'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('create/', views.employee_create, name='employee_create'),
    path('<int:pk>/update/', views.employee_update, name='employee_update'),
    path('<int:pk>/toggle-active/', views.employee_toggle_active, name='employee_toggle_active'),
]
