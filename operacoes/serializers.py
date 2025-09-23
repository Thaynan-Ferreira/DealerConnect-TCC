# operacoes/serializers.py

from rest_framework import serializers
# Vamos importar os serializers que já criamos nos outros apps
from produtos.serializers import VeiculoSerializer
from usuarios.serializers import ClienteSerializer, UsuarioSerializer
from .models import Venda

class VendaSerializer(serializers.ModelSerializer):
    """
    Este serializer transforma os dados de uma Venda em um formato JSON rico.
    Em vez de mostrar apenas os IDs, ele "aninha" as informações completas
    do cliente, do veículo e do vendedor, usando os serializers que já tínhamos.
    """
    # Aqui está a chave: aninhando os serializers.
    # 'read_only=True' significa que esses campos são apenas para leitura.
    # Não usaremos este endpoint para criar vendas (por enquanto).
    cliente = ClienteSerializer(read_only=True)
    veiculo = VeiculoSerializer(read_only=True)
    vendedor = UsuarioSerializer(read_only=True)

    class Meta:
        model = Venda
        # Definimos todos os campos que queremos que apareçam no JSON final.
        fields = [
            'id', 
            'data_venda', 
            'valor_final', 
            'tipo_pagamento', 
            'cliente', 
            'veiculo', 
            'vendedor'
        ]