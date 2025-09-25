from rest_framework import serializers
from .models import Pessoa, Cliente, Usuario

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ['id', 'nome', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'idade', 'lead_score']

class ClienteSerializer(serializers.ModelSerializer):
    # Usamos o PessoaSerializer para aninhar os dados da pessoa dentro do cliente
    pessoa = PessoaSerializer(read_only=True)
    classificacao = serializers.CharField(source='get_classificacao_display', read_only=True)
    # Adicionamos o 'get_situacao_display' para mostrar o texto amigável
    situacao = serializers.CharField(source='get_situacao_display', read_only=True)


    class Meta:
        model = Cliente
        # O ID do cliente é o mesmo da pessoa, então usamos 'pessoa_id'
        fields = ['pessoa_id', 'pessoa', 'classificacao', 'situacao']

class UsuarioSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ['pessoa_id', 'perfil', 'pessoa']