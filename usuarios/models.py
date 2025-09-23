# usuarios/models.py
from django.db import models

class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    cpf_cnpj = models.CharField(max_length=20, unique=True, verbose_name="CPF/CNPJ")
    email = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    # Trocamos data_nascimento por idade
    idade = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

class Cliente(models.Model):
    pessoa = models.OneToOneField(
        Pessoa, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    # Removido o ManyToMany com Segmento daqui

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