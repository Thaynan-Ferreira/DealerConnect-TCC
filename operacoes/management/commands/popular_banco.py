import os
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from produtos.models import Segmento, Veiculo
from usuarios.models import Pessoa, Cliente, Usuario
from operacoes.models import Venda
import re

def limpar_cpf(cpf_cnpj):
    return re.sub(r'[^0-9]', '', str(cpf_cnpj))

class Command(BaseCommand):
    help = 'Limpa e popula o banco de dados com dados reais e sintéticos'

    # Removi o @transaction.atomic daqui para controlar as transações manualmente
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Limpando o banco de dados...'))
        # A limpeza precisa ser feita em uma única transação
        with transaction.atomic():
            Venda.objects.all().delete()
            Cliente.objects.all().delete()
            Usuario.objects.all().delete()
            Pessoa.objects.all().delete()
            Veiculo.objects.all().delete()
            Segmento.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Banco de dados limpo.'))
        
        self.stdout.write(self.style.SUCCESS('Iniciando o processo de povoamento...'))
        self.importar_segmentos_e_veiculos()
        
        clientes_reais_df = self.importar_pessoas_reais()
        self.gerar_leads_sinteticos(clientes_reais_df)
        self.importar_vendas()

        self.stdout.write(self.style.SUCCESS('Banco de dados povoado com sucesso!'))

    def importar_segmentos_e_veiculos(self):
        self.stdout.write('1/4 - Importando Segmentos e Veículos...')
        caminho_csv = os.path.join(os.getcwd(), 'modelos_segmentados.csv')
        df = pd.read_csv(caminho_csv, encoding='utf-8-sig')
        for _, row in df.iterrows():
            Segmento.objects.get_or_create(nome_segmento=row['Segmento'])
            Veiculo.objects.get_or_create(modelo=row['Modelo'], defaults={'segmento': Segmento.objects.get(nome_segmento=row['Segmento']), 'marca': 'Honda'})
        self.stdout.write(self.style.SUCCESS(f'{Veiculo.objects.count()} veículos importados.'))

    def importar_pessoas_reais(self):
        self.stdout.write('2/4 - Importando Pessoas e Clientes Reais...')
        caminho_csv = os.path.join(os.getcwd(), 'tabela_pessoa_para_banco.csv')
        df = pd.read_csv(caminho_csv, encoding='utf-8-sig')

        clientes_reais_df = df[df['Tipo'] == 'Cliente'].copy()
        clientes_reais_df['Municipio'] = clientes_reais_df['Municipio'].fillna('Desconhecido').replace('', 'Desconhecido')
        clientes_reais_df.dropna(subset=['Idade'], inplace=True)
        
        np.random.seed(42)
        media_compradores = 7.5
        desvio_compradores = 1.5
        scores_reais = np.random.normal(loc=media_compradores, scale=desvio_compradores, size=len(clientes_reais_df))
        clientes_reais_df['lead_score'] = np.clip(scores_reais, 1, 10).astype(int)

        for _, row in df.iterrows():
            # Cada tentativa de criar uma pessoa agora está em sua própria "caixa de transação".
            try:
                with transaction.atomic(): # Inicia a "caixa"
                    cpf_limpo = limpar_cpf(row['CPF'])
                    if not cpf_limpo or pd.isna(row['Nome']) or row['Nome'].lower() == 'nan':
                        continue
                    
                    score_row = clientes_reais_df.loc[clientes_reais_df['CPF'].apply(limpar_cpf) == cpf_limpo, 'lead_score']
                    score = score_row.iloc[0] if not score_row.empty else 5

                    pessoa = Pessoa.objects.create(
                        cpf_cnpj=cpf_limpo, nome=row['Nome'], email=row['Email'], telefone=row['Telefone'],
                        endereco=row['Municipio'] if pd.notna(row['Municipio']) else 'Desconhecido',
                        idade=int(row['Idade']) if pd.notna(row['Idade']) else None,
                        lead_score=score
                    )
                    
                    if row['Tipo'] == 'Cliente':
                        Cliente.objects.create(pessoa=pessoa)
                    elif row['Tipo'] == 'Usuario':
                        Usuario.objects.create(pessoa=pessoa, senha_hash='senha_padrao', perfil='VENDEDOR')
            
            except IntegrityError:
                # Se der erro aqui dentro, apenas esta "caixa" é descartada.
                # O script pode continuar para a próxima pessoa com uma "caixa" limpa.
                self.stdout.write(self.style.WARNING(f"Pessoa com CPF {limpar_cpf(row['CPF'])} ou Email {row['Email']} já existe. Pulando."))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'{Pessoa.objects.count()} pessoas reais importadas.'))
        return clientes_reais_df

    def gerar_leads_sinteticos(self, clientes_reais_df):
        self.stdout.write('3/4 - Gerando Leads Sintéticos (Não-Compradores)...')
        if clientes_reais_df.empty:
            self.stdout.write(self.style.WARNING("Nenhum cliente real encontrado para basear a geração de leads sintéticos. Pulando esta etapa."))
            return
        
        num_falsos = len(clientes_reais_df)
        np.random.seed(42)
        idades_falsas = np.random.normal(loc=clientes_reais_df['Idade'].mean(), scale=clientes_reais_df['Idade'].std(), size=num_falsos).astype(int)
        idades_falsas = np.clip(idades_falsas, 18, 80)
        municipios_falsos = np.random.choice(clientes_reais_df['Municipio'].unique(), size=num_falsos)
        media_nao_compradores = 3.5
        desvio_nao_compradores = 1.5
        scores_falsos = np.random.normal(loc=media_nao_compradores, scale=desvio_nao_compradores, size=num_falsos)
        scores_falsos = np.clip(scores_falsos, 1, 10).astype(int)
        novos_leads = []
        for i in range(num_falsos):
            novos_leads.append(Pessoa(
                nome=f"Lead Sintético {i}", cpf_cnpj=f"000000000{i:02}",
                endereco=municipios_falsos[i], idade=idades_falsas[i], lead_score=scores_falsos[i]
            ))
        Pessoa.objects.bulk_create(novos_leads)
        self.stdout.write(self.style.SUCCESS(f'{len(novos_leads)} leads sintéticos criados.'))

    def importar_vendas(self):
        self.stdout.write('4/4 - Importando Vendas...')
        caminho_csv = os.path.join(os.getcwd(), 'vendas_processado.csv')
        df_vendas = pd.read_csv(caminho_csv, encoding='utf-8-sig')
        pessoa_sistema, _ = Pessoa.objects.get_or_create(cpf_cnpj='000SYSTEM000', defaults={'nome': 'Sistema / CNH'})
        vendedor_sistema, _ = Usuario.objects.get_or_create(pessoa=pessoa_sistema, defaults={'senha_hash': 'sistema', 'perfil': 'SISTEMA'})
        for _, row in df_vendas.iterrows():
            cliente_obj = Cliente.objects.filter(pessoa__nome=row['Cliente']).first()
            veiculo_obj = Veiculo.objects.filter(modelo=row['Veículo']).first()
            vendedor_obj = Usuario.objects.filter(pessoa__nome=row['Vendedor']).first() or vendedor_sistema
            if cliente_obj and veiculo_obj:
                Venda.objects.create(
                    cliente=cliente_obj, veiculo=veiculo_obj, vendedor=vendedor_obj,
                    data_venda=row['Data'], valor_final=0, tipo_pagamento=row['Forma de venda']
                )
        self.stdout.write(self.style.SUCCESS(f'{Venda.objects.count()} vendas importadas.'))
