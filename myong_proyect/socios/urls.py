from django.urls import path
from socios.views import detalle_socio, lista_socios, alta_socio, pagos_socio_current_year, pagos_socio_by_year
from socios.api_views import check_dni_api
urlpatterns = [
    path('<uuid:socio_id>/', detalle_socio, name='detalle_socio'),
    path('', lista_socios, name='lista_socios'),
    path('alta/', alta_socio, name='alta_socio'),
    path('<uuid:socio_id>/pagos/<int:year>', pagos_socio_by_year, name='pagos_socio_by_year'),
    path('<uuid:socio_id>/pagos/', pagos_socio_current_year, name='pagos_socio_current_year'), 
    path('check_dni/', check_dni_api, name='check_dni'),
]