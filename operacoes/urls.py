from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendaViewSet

# Cria um roteador para gerenciar as URLs da API automaticamente.
router = DefaultRouter()
# Registra nossa VendaViewSet na rota 'vendas'.
router.register(r'vendas', VendaViewSet, basename='venda')

# As URLs do nosso app serão as que o roteador gerar.
urlpatterns = [
    path('', include(router.urls)),
]