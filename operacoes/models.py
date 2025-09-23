# operacoes/models.py

from django.db import models

class Venda(models.Model):
    class TipoPagamento(models.TextChoices):
        FINANCIAMENTO = 'FIN', 'Financiamento'
        A_VISTA = 'AV', 'À Vista'
        CONSORCIO = 'CONS', 'Consórcio'

    cliente = models.ForeignKey('usuarios.Cliente', on_delete=models.PROTECT, related_name='vendas')
    veiculo = models.ForeignKey('produtos.Veiculo', on_delete=models.PROTECT, related_name='vendas')
    vendedor = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, related_name='vendas_realizadas')
    data_venda = models.DateTimeField(auto_now_add=True)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pagamento = models.CharField(max_length=50, choices=TipoPagamento.choices, blank=True)

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.pessoa.nome}"

class Atendimento(models.Model):
    cliente = models.ForeignKey('usuarios.Cliente', on_delete=models.CASCADE, related_name='atendimentos')
    atendente = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='atendimentos_realizados')
    data_atendimento = models.DateTimeField(auto_now_add=True)
    canal = models.CharField(max_length=50)
    descricao = models.TextField()

    def __str__(self):
        return f"Atendimento para {self.cliente.pessoa.nome} em {self.data_atendimento.strftime('%d/%m/%Y')}"