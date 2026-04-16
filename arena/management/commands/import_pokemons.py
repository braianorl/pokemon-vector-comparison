import time
import requests
from django.core.management.base import BaseCommand
from arena.models import Pokemon

class Command(BaseCommand):
    help = 'Importa TUDO: Sprites, Stats, Moves e Descrição'

    def handle(self, *args, **kwargs):
        self.stdout.write("🔥 Iniciando Captura Completa (Isso pode demorar um pouco)...")

        # Dica: Mude o range(1, 1026) se quiser baixar todos
        # Vou deixar 20 aqui pra você testar rápido primeiro
        for poke_id in range(1, 1026): 
            try:
                # --- REQUISIÇÃO 1: DADOS DE BATALHA ---
                r_main = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke_id}')
                if r_main.status_code != 200: continue
                data_main = r_main.json()

                # --- REQUISIÇÃO 2: DADOS DE LORE (DESCRIÇÃO) ---
                # A descrição fica em outro endereço na API (pokemon-species)
                r_species = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{poke_id}')
                data_species = r_species.json() if r_species.status_code == 200 else {}

                # 1. Processando a Descrição (Pega a primeira em Inglês)
                description = "No description available."
                if data_species:
                    for entry in data_species.get('flavor_text_entries', []):
                        if entry['language']['name'] == 'en':
                            # Limpa quebras de linha estranhas do texto original
                            description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                            break

                # 2. Processando Sprites
                sprites = data_main['sprites']
                icon = sprites['front_default']
                animated = sprites.get('other', {}).get('showdown', {}).get('front_default') or icon
                hd = sprites.get('other', {}).get('home', {}).get('front_default')

                # 3. Stats e Tipos
                stats = {s['stat']['name']: s['base_stat'] for s in data_main['stats']}
                types = data_main['types']
                t1 = types[0]['type']['name']
                t2 = types[1]['type']['name'] if len(types) > 1 else None

                # 4. A MOCHILA MÁGICA (JSON)
                # Agora incluindo MOVES e DESCRIPTION
                extra_data = {
                    'height': data_main['height'],
                    'weight': data_main['weight'],
                    'abilities': [a['ability']['name'] for a in data_main['abilities']], # Passivas
                    'moves': [m['move']['name'] for m in data_main['moves']], # <--- AQUI ESTÃO OS GOLPES!
                    'description': description, # <--- AQUI ESTÁ A HISTÓRIA!
                    'capture_rate': data_species.get('capture_rate'),
                    'growth_rate': data_species.get('growth_rate', {}).get('name')
                }

                # 5. Salvar
                Pokemon.objects.update_or_create(
                    id=poke_id,
                    defaults={
                        'name': data_main['name'].capitalize(),
                        'hp': stats['hp'],
                        'attack': stats['attack'],
                        'defense': stats['defense'],
                        'special_attack': stats['special-attack'],
                        'special_defense': stats['special-defense'],
                        'speed': stats['speed'],
                        'total': sum(stats.values()),
                        'type_1': t1,
                        'type_2': t2,
                        'sprite_icon': icon,
                        'sprite_animated': animated,
                        'sprite_hd': hd,
                        'data': extra_data # Salva o JSON gordo
                    }
                )

                self.stdout.write(f"✅ #{poke_id} {data_main['name']} - Completo!")
                time.sleep(0.6) # Pausa de cortesia

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erro {poke_id}: {e}"))