from django.contrib import admin
from .models import Categoria, Libro, Pedido

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'categoria', 'precio', 'stock', 'fecha_creacion']
    list_filter = ['categoria', 'fecha_creacion']
    search_fields = ['titulo', 'autor']
    list_editable = ['precio', 'stock']
    ordering = ['-fecha_creacion']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'libro', 'cantidad', 'total', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['usuario__username', 'libro__titulo']
    list_editable = ['estado']
    ordering = ['-fecha_creacion']