from rest_framework import serializers
from .models import Veiculo, Segmento

class SegmentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segmento
        fields = ['id', 'nome_segmento']

class VeiculoSerializer(serializers.ModelSerializer):
    # Mostra o nome do segmento em vez de apenas o ID
    segmento = SegmentoSerializer(read_only=True)

    class Meta:
        model = Veiculo
        fields = ['id', 'marca', 'modelo', 'ano', 'preco', 'chassi', 'segmento']