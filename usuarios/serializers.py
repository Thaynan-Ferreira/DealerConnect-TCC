from rest_framework import serializers
from .models import Pessoa, Cliente, Usuario

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ['id', 'nome', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'idade']

class ClienteSerializer(serializers.ModelSerializer):
    # Usamos o PessoaSerializer para aninhar os dados da pessoa dentro do cliente
    pessoa = PessoaSerializer(read_only=True)

    class Meta:
        model = Cliente
        # O ID do cliente é o mesmo da pessoa, então usamos 'pessoa_id'
        fields = ['pessoa_id', 'pessoa']

class UsuarioSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ['pessoa_id', 'perfil', 'pessoa']