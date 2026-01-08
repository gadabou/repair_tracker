from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from dashboard.views import home_redirect, CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('tickets/', include('tickets.urls')),
    path('accounts/', include('accounts.urls')),
    path('assets/', include('assets.urls')),
    path('employees/', include('employees.urls')),
    path('api/', include('config.api_urls')),

    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
