from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters # Importamos o módulo de filtros do DRF
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este endpoint da API permite visualizar e buscar clientes.
    
    Você pode filtrar os resultados usando os seguintes parâmetros na URL:
    - ?pessoa__nome__icontains=joao  (Busca por parte do nome, ignorando maiúsculas/minúsculas)
    - ?pessoa__cpf_cnpj=12345678900 (Busca por um CPF exato)
    - ?search=joao                  (Busca geral por nome ou CPF)
    """
    queryset = Cliente.objects.select_related('pessoa').all().order_by('pessoa__nome')
    serializer_class = ClienteSerializer
    
    # --- A MÁGICA ACONTECE AQUI ---
    # Ativamos os "motores" de filtro e busca que o DRF vai usar.
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Aqui definimos os campos exatos que o `django-filter` pode usar.
    # O formato 'pessoa__nome' permite filtrar pelo campo 'nome' do model relacionado 'Pessoa'.
    filterset_fields = ['pessoa__cpf_cnpj']
    
    # Aqui configuramos a busca. Ele vai procurar nos campos 'nome' e 'cpf_cnpj'
    # da tabela relacionada 'Pessoa'.
    search_fields = ['pessoa__nome', 'pessoa__cpf_cnpj']