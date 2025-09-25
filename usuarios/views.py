# --- Imports necessários para a API completa ---
from django.conf import settings
import os
from rest_framework import viewsets, status # Adicionamos 'status' para respostas de erro
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action # Essencial para criar endpoints customizados
from rest_framework.response import Response # Para enviar respostas JSON customizadas
import joblib # Para carregar o modelo de ML
import pandas as pd # Para formatar os dados para o modelo
from .models import Cliente, Pessoa # Importamos Pessoa para acessar seus dados
from .serializers import ClienteSerializer



# Trocamos ReadOnlyModelViewSet por ModelViewSet.
# Isso "desbloqueia" as ações de criar, editar e apagar.
class ClienteViewSet(viewsets.ModelViewSet):
    """
    Este endpoint da API permite visualizar, buscar, classificar e ATUALIZAR clientes.
    """
    queryset = Cliente.objects.select_related('pessoa').all().order_by('pessoa__nome')
    serializer_class = ClienteSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pessoa__cpf_cnpj']
    search_fields = ['pessoa__nome', 'pessoa__cpf_cnpj']
    
    # --- CÓDIGO NOVO (Ação 'classificar') ---
    # Este é o código que cria o endpoint para usar o modelo de ML.
    @action(detail=True, methods=['post'])
    def classificar(self, request, pk=None):
        """
        Endpoint que executa o modelo de ML para classificar o potencial
        de um cliente específico, usando seus dados REAIS do banco.
        """
        try:
            # Carrega o modelo treinado que salvamos na raiz do projeto
            caminho_modelo = os.path.join(settings.BASE_DIR, 'ml_models', 'modelo_classificacao_cliente.joblib')
            pipeline = joblib.load(caminho_modelo)
            cliente = self.get_object()
            
            # Prepara os dados do cliente no formato que o modelo espera
            dados_para_previsao = pd.DataFrame({
                'Idade': [cliente.pessoa.idade],
                'Municipio': [cliente.pessoa.endereco],
                'lead_score': [cliente.pessoa.lead_score] # Usa o dado real do banco
            })
            
            # Faz a previsão (retorna 0 ou 1)
            previsao_numerica = pipeline.predict(dados_para_previsao)[0]
            
            # Traduz o resultado numérico para o texto que definimos no model
            if previsao_numerica == 1:
                cliente.classificacao = Cliente.ClassificacaoCliente.ALTO_POTENCIAL
                resultado_texto = 'Potencial Alto'
            else:
                cliente.classificacao = Cliente.ClassificacaoCliente.POTENCIAL_PADRAO
                resultado_texto = 'Potencial Padrão'
            
            # Salva o resultado no banco de dados
            cliente.save()
            
            return Response({'status': 'sucesso', 'classificacao': resultado_texto})

        except FileNotFoundError:
            return Response({'erro': 'Arquivo do modelo não encontrado.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Este é o código que permite ao vendedor mudar o status do atendimento.
    @action(detail=True, methods=['patch'])
    def atualizar_situacao(self, request, pk=None):
        """
        Endpoint específico para atualizar APENAS a situação de um cliente.
        Espera um corpo de requisição como: { "situacao": "NEGOCIANDO" }
        """
        cliente = self.get_object()
        nova_situacao = request.data.get('situacao')

        # Validação para garantir que a situação enviada é uma das opções válidas
        opcoes_validas = [choice[0] for choice in Cliente.SituacaoAtendimento.choices]
        if nova_situacao not in opcoes_validas:
            return Response(
                {'erro': f"Situação inválida. Opções são: {opcoes_validas}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        cliente.situacao = nova_situacao
        cliente.save()
        
        serializer = self.get_serializer(cliente)
        return Response(serializer.data)
