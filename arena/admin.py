from django.contrib import admin
from django.utils.html import format_html
from .models import Move, Pokemon

class PokemonAdmin(admin.ModelAdmin):
    # 1. Quais colunas aparecem na lista?
    list_display = ('id', 'show_sprite', 'name', 'type_1', 'type_2', 'total')
    
    # 2. Por onde ele deve ordenar? (Crescente pelo ID)
    ordering = ('id',) 
    
    # 3. Adiciona uma BARRA DE PESQUISA (Busca por nome ou tipo)
    search_fields = ('name', 'type_1')
    
    # 4. Adiciona FILTROS laterais
    list_filter = ('type_1',)

    # Função extra para mostrar a imagem
    def show_sprite(self, obj):
        if obj.sprite_icon:
            return format_html('<img src="{}" width="40" />', obj.sprite_icon)
        return "-"
    show_sprite.short_description = "Ícone"

class MoveAdmin(admin.ModelAdmin):
    # O que mostrar na lista
    list_display = ('name', 'type', 'category', 'power', 'accuracy', 'pp')
    
    # Filtros laterais (Ótimo para balancear o jogo)
    list_filter = ('type', 'category') 
    
    # Barra de busca
    search_fields = ('name',)
    
    # Ordenar por nome
    ordering = ('name',)

# Registra os dois
admin.site.register(Pokemon, PokemonAdmin)
admin.site.register(Move, MoveAdmin)
