from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import date
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken



from .models import Socio, Pago
from .serializers import SocioSerializer, SocioCreateSerializer, PagoSerializer
from .dni_utils import check_dni  # Función de validación de DNI 


class SocioViewSet(viewsets.ModelViewSet):
    """
    Proporciona operaciones CRUD completas para el modelo Socio.
    Hereda de ModelViewSet que incluye: list, create, retrieve, update, destroy
    """
    queryset = Socio.objects.select_related('direccion').prefetch_related('tutor_legal')
    
    def get_serializer_class(self):
        """Usa diferente serializer según la acción"""
        if self.action in ['create', 'update', 'partial_update']:
            return SocioCreateSerializer
        return SocioSerializer

class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para consultar pagos.
    Soporta filtrado por socio y año mediante query params.
    """
    serializer_class = PagoSerializer
    
    def get_queryset(self):
        queryset = Pago.objects.select_related('socio')
        
        # Filtrado opcional por parámetros URL
        socio_id = self.request.query_params.get('socio')
        year = self.request.query_params.get('year', date.today().year)
        
        if socio_id:
            queryset = queryset.filter(socio__id=socio_id)
        
        return queryset.filter(anio=year)

# Endpoint funcional adicional (alternativa a acciones de ViewSet)
@api_view(['GET'])
def pagos_por_socio(request, socio_id):
    """
    Endpoint personalizado para obtener pagos de un socio específico.
    Accesible en: /api/socios/<uuid>/pagos/
    """
    year = request.query_params.get('year', date.today().year)
    pagos = Pago.objects.filter(socio__id=socio_id, anio=year).order_by('mes')
    
    return Response({
        'socio_id': str(socio_id),
        'year': year,
        'pagos': PagoSerializer(pagos, many=True).data,
        'total_meses': pagos.count(),
        'total_pagado': sum(p.monto for p in pagos if p.pagado),
    })

# Endpoint para validar DNI (ejemplo de función independiente)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Sin autenticación para este endpoint
def check_dni_api(request):
    """
    Endpoint para validar un DNI español.
    Recibe un JSON con {"documento": "12345678A"} y devuelve resultado de validación.
    """    
    documento = request.data.get('documento')
    if not documento:
        return Response({"error": "Campo 'documento' es requerido"}, status=status.HTTP_400_BAD_REQUEST) #Dni no proporcionado

    resultado = check_dni(documento)


    # Si el DNI es válido → 200
    if resultado["valido"]:
        return Response(resultado, status=status.HTTP_200_OK)

    # Si es inválido → 400 (según criterio de aceptación)
    return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

class SocioListCreateView(generics.ListCreateAPIView):
    """
    GET: Listar todos los socios (requiere autenticación)
    POST: Crear nuevo socio (requiere autenticación)
    """
    queryset = Socio.objects.all()
    serializer_class = SocioSerializer
    permission_classes = [permissions.IsAuthenticated]

class SocioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtener detalle de un socio
    PUT/PATCH: Actualizar socio
    DELETE: Eliminar socio
    """
    queryset = Socio.objects.all()
    serializer_class = SocioSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

class PerfilView(APIView):
    """
    Endpoint para obtener información del usuario autenticado
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'usuario': request.user.username,
            'email': request.user.email,
            'socio_id': getattr(request.user, 'socio_id', None)
        })

class LogoutView(APIView):
    """
    POST: Invalidar el refresh token (logout)
    Requiere enviar el refresh token en el body
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Añade a lista negra
            
            return Response(
                {'mensaje': 'Logout exitoso, token invalidado'}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
