import time
import requests
from django.core.management.base import BaseCommand
from arena.models import Move

class Command(BaseCommand):
    help = 'Importa Moves com dados de Batalha (Elifoot Mode)'

    def handle(self, *args, **kwargs):
        self.stdout.write("⚔️ Baixando Manual de Combate Avançado...")

        # Vamos pegar os golpes da Geração 1 (165 golpes)
        # Se quiser TUDO, mude para range(1, 920)
        for move_id in range(1, 920): 
            try:
                r = requests.get(f'https://pokeapi.co/api/v2/move/{move_id}')
                if r.status_code != 200: continue
                data = r.json()

                # 1. Tratando a Descrição
                desc = "No description."
                if data.get('flavor_text_entries'):
                    for entry in data['flavor_text_entries']:
                        if entry['language']['name'] == 'en':
                            desc = entry['flavor_text'].replace('\n', ' ')
                            break
                
                # 2. Tratando o Meta Data (O JSON complexo)
                # A API às vezes manda "meta": null, então precisamos garantir que seja um dict
                meta_data = data.get('meta') or {}

                # 3. Salva no Banco
                Move.objects.update_or_create(
                    name=data['name'],
                    defaults={
                        'type': data['type']['name'],
                        'category': data['damage_class']['name'], # Importante: Physical vs Special
                        'power': data['power'],
                        'accuracy': data['accuracy'],
                        'pp': data['pp'],
                        
                        # Novos campos estratégicos
                        'priority': data['priority'],
                        'target': data['target']['name'],
                        'effect_chance': data['effect_chance'],
                        'description': desc,
                        
                        # O JSON Puro com as regras de efeito
                        'mechanics': meta_data 
                    }
                )

                self.stdout.write(f"⚔️ {data['name']} - OK")
                time.sleep(0.3)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erro {move_id}: {e}"))
        
        self.stdout.write(self.style.SUCCESS('✨ Banco de Dados de Combate Pronto!'))