from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import SocioViewSet, PagoViewSet, pagos_por_socio, check_dni_api,SocioListCreateView, SocioDetailView, PerfilView 
from socios.api_views import LogoutView

# Crea el router y registra los ViewSets
router = DefaultRouter()
router.register(r'socios', SocioViewSet)      # Genera /api/socios/
router.register(r'pagos', PagoViewSet, basename='pago')  # Genera /api/pagos/

# Las URLs generadas incluyen:
# /socios/          -> list (GET), create (POST)
# /socios/{id}/     -> retrieve (GET), update (PUT/PATCH), destroy (DELETE)

urlpatterns = [
    path('', include(router.urls)),
    # Endpoint personalizado para pagos por socio
    path('socios/<uuid:socio_id>/pagos/', pagos_por_socio, name='api_pagos_socio'),
    # Endpoint para validar DNI
    path('check_dni/', check_dni_api, name='api_check_dni'),
    path('', SocioListCreateView.as_view(), name='socio-list'),
    path('<int:pk>/', SocioDetailView.as_view(), name='socio-detail'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]