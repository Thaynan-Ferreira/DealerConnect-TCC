from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count

from usuarios.models import Cliente, Pessoa

class DashboardStatsView(APIView):
    """
    Uma view somente leitura que calcula e retorna as principais
    estatísticas do sistema para o dashboard.
    """
    def get(self, request, format=None):
        try:
            # Contagem total de clientes (pessoas com o papel de cliente)
            total_clientes = Cliente.objects.count()

            # Contagem total de leads (todas as Pessoas que NÃO são clientes)
            total_leads = Pessoa.objects.exclude(cliente__isnull=False).count()

            # Agrupa os clientes pela situação e conta quantos há em cada grupo
            contagem_por_situacao = Cliente.objects.values('situacao').annotate(
                count=Count('situacao')
            ).order_by('-count') # Ordena do maior para o menor

            # Agrupa os clientes pela classificação do modelo de ML e conta
            contagem_por_classificacao = Cliente.objects.values('classificacao').annotate(
                count=Count('classificacao')
            ).order_by('-count')

            # Monta o objeto JSON final que será enviado ao front-end
            stats = {
                "total_clientes": total_clientes,
                "total_leads": total_leads,
                "contagem_por_situacao": list(contagem_por_situacao),
                "contagem_por_classificacao": list(contagem_por_classificacao),
            }
            
            return Response(stats, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)