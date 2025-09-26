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

# Este serializer é específico para a AÇÃO de criar um novo cliente.
class ClienteCreateSerializer(serializers.ModelSerializer):
    # Declaramos explicitamente os campos que virão do formulário do front-end.
    # Estes são os campos do model Pessoa.
    nome = serializers.CharField(source='pessoa.nome')
    cpf_cnpj = serializers.CharField(source='pessoa.cpf_cnpj')
    email = serializers.EmailField(source='pessoa.email', allow_blank=True, required=False)
    telefone = serializers.CharField(source='pessoa.telefone', allow_blank=True, required=False)
    endereco = serializers.CharField(source='pessoa.endereco', allow_blank=True, required=False)
    idade = serializers.IntegerField(source='pessoa.idade', required=False)
    lead_score = serializers.IntegerField(source='pessoa.lead_score', required=False)

    class Meta:
        model = Cliente
        # Os campos que este serializer vai "entender"
        fields = ['nome', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'idade', 'lead_score']

    def create(self, validated_data):
        """
        Esta é a função mágica. Quando a API recebe os dados, esta função é chamada.
        Ela separa os dados da Pessoa, cria o objeto Pessoa primeiro,
        e depois cria o objeto Cliente ligado a essa nova Pessoa.
        """
        pessoa_data = validated_data.pop('pessoa')
        pessoa = Pessoa.objects.create(**pessoa_data)
        cliente = Cliente.objects.create(pessoa=pessoa, **validated_data)
        return cliente