from django.contrib import admin
from .models import Pessoa, Cliente, Usuario

admin.site.register(Pessoa)
admin.site.register(Cliente)
admin.site.register(Usuario)