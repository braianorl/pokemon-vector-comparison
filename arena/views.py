from django.shortcuts import render
from .models import Pokemon
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def index(request):
    # 1. Tenta pegar o que o usuário digitou na busca (pelo nome 'q')
    query = request.GET.get('q') 

    if query:
        # 2. Se tiver busca, Filtra!
        # __icontains = "Contém o texto" (Ignora maiúscula/minúscula)
        pokemons = Pokemon.objects.filter(name__icontains=query)
    else:
        # 3. Se não tiver busca, mostra todos (ou os primeiros 20 pra não travar)
        pokemons = Pokemon.objects.all()[:20]

    return render(request, 'index.html', {'pokemons': pokemons})

# Nova view para busca dinâmica via HTMX
def search_pokemon(request):
    query = request.GET.get('q', '')
    
    if len(query) > 0:
        # Filtra pelo nome (insensível a maiúscula/minúscula)
        # Pega só os primeiros 5 pra caber no modal
        results = Pokemon.objects.filter(name__icontains=query)[:5]
    else:
        results = []

    # O segredo: Renderiza SÓ o pedacinho (partial), não o site todo
    return render(request, 'partials/search_results.html', {'pokemons': results})

# arena/views.py
def get_pokemon_details(request, id):
    pokemon = get_object_or_404(Pokemon, id=id)
    
    # Montamos o dicionário com tudo que seu JS precisa
    data = {
        'id': pokemon.id,
        'name': pokemon.name,
        'sprite': pokemon.sprite_animated or pokemon.sprite_icon,
        'types': [pokemon.type_1, pokemon.type_2] if pokemon.type_2 else [pokemon.type_1],
        'stats': {
            'hp': pokemon.hp,
            'attack': pokemon.attack,
            'defense': pokemon.defense,
            'special-attack': pokemon.special_attack,
            'special-defense': pokemon.special_defense,
            'speed': pokemon.speed,
            'total': pokemon.total
        },
        'height': pokemon.data.get('height'),
        'weight': pokemon.data.get('weight')
    }
    return JsonResponse(data)