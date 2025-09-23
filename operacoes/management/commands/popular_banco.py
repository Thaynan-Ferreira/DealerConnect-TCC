# operacoes/management/commands/popular_banco.py (VERSÃO CORRIGIDA)

import csv
import os
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from produtos.models import Segmento, Veiculo
from usuarios.models import Pessoa, Cliente, Usuario
from operacoes.models import Venda
import re

# Função para limpar CPF/CNPJ (remover pontos, traços, etc.)
def limpar_cpf(cpf_cnpj):
    return re.sub(r'[^0-9]', '', str(cpf_cnpj))

class Command(BaseCommand):
    help = 'Limpa as tabelas e popula o banco de dados com os dados dos arquivos CSV'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Limpando o banco de dados...'))
        # Limpa as tabelas na ordem correta para evitar erros de chave estrangeira
        Venda.objects.all().delete()
        Cliente.objects.all().delete()
        Usuario.objects.all().delete()
        Pessoa.objects.all().delete()
        Veiculo.objects.all().delete()
        Segmento.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Banco de dados limpo.'))
        
        self.stdout.write(self.style.SUCCESS('Iniciando o processo de povoamento...'))

        # --- ORDEM DE IMPORTAÇÃO ---
        self.importar_segmentos_e_veiculos()
        self.importar_pessoas_clientes_usuarios()
        self.importar_vendas()

        self.stdout.write(self.style.SUCCESS('Banco de dados povoado com sucesso!'))

    def importar_segmentos_e_veiculos(self):
        self.stdout.write('1/3 - Importando Segmentos e Veículos...')
        caminho_csv = os.path.join(os.getcwd(), 'modelos_segmentados.csv')
        
        # CORREÇÃO APLICADA: encoding='utf-8-sig'
        with open(caminho_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                segmento, _ = Segmento.objects.get_or_create(nome_segmento=row['Segmento'])
                Veiculo.objects.get_or_create(
                    modelo=row['Modelo'],
                    defaults={'segmento': segmento, 'marca': 'Honda'}
                )
        self.stdout.write(self.style.SUCCESS('Segmentos e Veículos importados.'))

    def importar_pessoas_clientes_usuarios(self):
        self.stdout.write('2/3 - Importando Pessoas, Clientes e Usuários...')
        caminho_csv = os.path.join(os.getcwd(), 'tabela_pessoa_para_banco.csv')

        # CORREÇÃO APLICADA: encoding='utf-8-sig'
        with open(caminho_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # CORREÇÃO PARA NOMES DAS COLUNAS: '\ufeffNome' e ' CPF' (com espaço)
                nome_coluna = next(iter(row)) # Pega o nome da primeira coluna, seja ele qual for
                nome = row[nome_coluna]
                cpf_bruto = row.get('CPF') or row.get(' CPF') # Tenta pegar com e sem espaço

                if not cpf_bruto or not nome or nome.lower() == 'nan':
                    continue

                cpf_limpo = limpar_cpf(cpf_bruto)
                if not cpf_limpo:
                    continue

                try:
                    pessoa, created = Pessoa.objects.get_or_create(
                        cpf_cnpj=cpf_limpo,
                        defaults={
                            'nome': nome,
                            'email': row['Email'] if row['Email'] else None,
                            'telefone': row['Telefone'],
                            'endereco': row['Municipio'],
                            'idade': int(float(row['Idade'])) if row['Idade'] else None,
                        }
                    )
                    
                    if row['Tipo'] == 'Cliente':
                        Cliente.objects.get_or_create(pessoa=pessoa)
                    elif row['Tipo'] == 'Usuario':
                        Usuario.objects.get_or_create(
                            pessoa=pessoa,
                            defaults={
                                'senha_hash': 'senha_padrao_123',
                                'perfil': Usuario.Perfil.VENDEDOR
                            }
                        )
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(f'Pessoa com CPF {cpf_limpo} já existe ou e-mail duplicado. Pulando.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro ao processar linha: {row} - {e}"))
        self.stdout.write(self.style.SUCCESS('Pessoas, Clientes e Usuários importados.'))

    @transaction.atomic
    def importar_vendas(self):
        self.stdout.write('3/3 - Importando Vendas...')
        caminho_csv = os.path.join(os.getcwd(), 'vendas_processado.csv')
        
        pessoa_sistema, _ = Pessoa.objects.get_or_create(
            cpf_cnpj='00000000000', defaults={'nome': 'Sistema / CNH'}
        )
        vendedor_sistema, _ = Usuario.objects.get_or_create(
            pessoa=pessoa_sistema, defaults={'senha_hash': 'sistema', 'perfil': Usuario.Perfil.SISTEMA}
        )

        # CORREÇÃO APLICADA: encoding='utf-8-sig'
        with open(caminho_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cliente_nome = row['Cliente']
                    vendedor_nome = row['Vendedor']
                    veiculo_modelo = row['Veículo']
                    
                    if not cliente_nome or not veiculo_modelo:
                        continue

                    cliente_obj = Cliente.objects.filter(pessoa__nome=cliente_nome).first()
                    if not cliente_obj:
                        self.stdout.write(self.style.WARNING(f"Cliente '{cliente_nome}' não encontrado. Pulando venda."))
                        continue
                    
                    veiculo_obj = Veiculo.objects.filter(modelo=veiculo_modelo).first()
                    if not veiculo_obj:
                        self.stdout.write(self.style.WARNING(f"Veículo '{veiculo_modelo}' não encontrado. Pulando venda."))
                        continue
                    
                    vendedor_obj = Usuario.objects.filter(pessoa__nome=vendedor_nome).first()
                    if not vendedor_obj:
                        vendedor_obj = vendedor_sistema

                    Venda.objects.create(
                        cliente=cliente_obj,
                        veiculo=veiculo_obj,
                        vendedor=vendedor_obj,
                        data_venda=row['Data'],
                        valor_final=0, 
                        tipo_pagamento=row['Forma de venda']
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro ao importar venda: {row} - {e}"))
        self.stdout.write(self.style.SUCCESS('Vendas importadas.'))