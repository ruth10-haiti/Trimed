"""
URL configuration for trimed_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

# Configuration Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Trimed Backend API",
        default_version='v1',
        description="API pour l'application de gestion hospitalière Trimed",
        contact=openapi.Contact(email="trimedhaiti@gmail.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('Trimedh/', admin.site.urls),
    # Endpoints de santé
    path('', views.api_info, name='api-info'),
    path('health/', views.health_check, name='health-check'),
    # Documentation API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # API endpoints
    path('api/tenants/', include('gestion_tenants.urls')),
    path('api/comptes/', include('comptes.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/medical/', include('medical.urls')),
    path('api/medicaments/', include('gestion_medicaments.urls')),
    path('api/rendez-vous/', include('rendez_vous.urls')),
    path('api/facturation/', include('facturation.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/hospitalisation/', include('hospitalisation.urls')),
path('api/salles-medicales/', include('salles_medicales.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)