from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Veiculo
from .serializers import VeiculoSerializer

class VeiculoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este endpoint da API permite visualizar e buscar veículos.

    Você pode filtrar os resultados usando os seguintes parâmetros na URL:
    - ?segmento=1              (Filtra por ID do segmento)
    - ?search=cg               (Busca por parte do modelo ou marca)
    """
    queryset = Veiculo.objects.select_related('segmento').all().order_by('modelo')
    serializer_class = VeiculoSerializer

    # --- MESMA LÓGICA DA VIEW DE CLIENTES ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Permitimos filtrar exatamente pelo ID do segmento a que o veículo pertence.
    filterset_fields = ['segmento']
    
    # A busca geral vai procurar tanto na marca quanto no modelo.
    search_fields = ['marca', 'modelo']