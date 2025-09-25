# usuarios/models.py
from django.db import models

class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    cpf_cnpj = models.CharField(max_length=20, unique=True, verbose_name="CPF/CNPJ")
    email = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    idade = models.IntegerField(null=True, blank=True)
    lead_score = models.IntegerField(
        default=5, 
        verbose_name="Pontuação do Lead"
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

class Cliente(models.Model):
    # Classe interna para as opções de Situação do Atendimento
    class SituacaoAtendimento(models.TextChoices):
        NOVO_CONTATO = 'NOVO', 'Novo Contato'
        EM_NEGOCIACAO = 'NEGOCIANDO', 'Em Negociação'
        VENDA_REALIZADA = 'VENDIDO', 'Venda Realizada'
        PERDIDO = 'PERDIDO', 'Perdido'

    # Classe interna para as opções de Classificação
    class ClassificacaoCliente(models.TextChoices):
        ALTO_POTENCIAL = 'ALTO', 'Potencial Alto'
        POTENCIAL_PADRAO = 'PADRAO', 'Potencial Padrão'
        NAO_CLASSIFICADO = 'N/A', 'Não Classificado'

    pessoa = models.OneToOneField(
        Pessoa, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    classificacao = models.CharField(
        max_length=10,
        choices=ClassificacaoCliente.choices,
        default=ClassificacaoCliente.NAO_CLASSIFICADO,
        verbose_name="Classificação de Potencial"
    )

    # Este campo armazenará o status atual do relacionamento com o cliente.
    situacao = models.CharField(
        max_length=10,
        choices=SituacaoAtendimento.choices,
        default=SituacaoAtendimento.NOVO_CONTATO,
        verbose_name="Situação do Atendimento"
    )
    
    @property
    def nome(self):
        return self.pessoa.nome

    def __str__(self):
        return self.pessoa.nome

class Usuario(models.Model):
    class Perfil(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        ANALISTA = 'ANALISTA', 'Analista'
        VENDEDOR = 'VENDEDOR', 'Vendedor'
        SISTEMA = 'SISTEMA', 'Sistema'

    pessoa = models.OneToOneField(
        Pessoa, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    senha_hash = models.CharField(max_length=255)
    perfil = models.CharField(max_length=50, choices=Perfil.choices)
    
    @property
    def nome(self):
        return self.pessoa.nome

    def __str__(self):
        return self.pessoa.nome