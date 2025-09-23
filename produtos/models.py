# produtos/models.py
from django.db import models

class Segmento(models.Model):
    nome_segmento = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome_segmento

class Veiculo(models.Model):
    marca = models.CharField(max_length=100, default="Honda")
    modelo = models.CharField(max_length=100)
    ano = models.IntegerField(null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    chassi = models.CharField(max_length=50, unique=True, null=True, blank=True)
    # Relacionamento ForeignKey para Segmento
    segmento = models.ForeignKey(Segmento, on_delete=models.SET_NULL, null=True, blank=True, related_name='veiculos')

    def __str__(self):
        return f"{self.marca} {self.modelo}"