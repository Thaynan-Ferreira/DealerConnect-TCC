from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Venda
from .serializers import VendaSerializer


class VendaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este endpoint da API permite visualizar e filtrar as vendas realizadas.
    
    É um endpoint crucial, pois fornece os dados que serão usados para
    treinar o modelo de Machine Learning.
    
    Exemplos de filtro na URL:
    - ?cliente=5              (Filtra todas as vendas de um cliente específico)
    - ?vendedor=10             (Filtra todas as vendas de um vendedor específico)
    """
    serializer_class = VendaSerializer
    
    # Ativamos o "motor" de filtros do DjangoFilterBackend
    filter_backends = [DjangoFilterBackend]
    
    # Criamos a "lista branca" de campos pelos quais podemos filtrar.
    # Podemos filtrar pelo ID do cliente, do veículo ou do vendedor.
    filterset_fields = ['cliente', 'veiculo', 'vendedor']

    def get_queryset(self):
        """
        Esta função é responsável por buscar os dados no banco de dados.
        Nós a otimizamos para que, em uma única consulta, ela já traga
        todas as informações relacionadas (cliente, pessoa, veículo, etc.),
        tornando a API muito mais rápida e eficiente.
        """
        return Venda.objects.select_related(
            'cliente__pessoa', 
            'veiculo__segmento', 
            'vendedor__pessoa'
        ).all().order_by('-data_venda') # Ordena da mais recente para a mais antiga