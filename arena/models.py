# arena/models.py
from django.db import models

class Pokemon(models.Model):
    
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    
    # 1. Para a Busca (Leve, Pixel Art)
    sprite_icon = models.URLField(max_length=500, blank=True, null=True)
    
    # 2. Para o Detalhe (Animado, Showdown)
    sprite_animated = models.URLField(max_length=500, blank=True, null=True)
    
    # (Opcional) Mantenha a HD se quiser usar de fundo ou capa
    sprite_hd = models.URLField(max_length=500, blank=True, null=True)

    # ...Stats (hp, attack...)
    hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    special_attack = models.IntegerField()
    special_defense = models.IntegerField()
    speed = models.IntegerField()
    total = models.IntegerField(default=0)
    
    type_1 = models.CharField(max_length=50)
    type_2 = models.CharField(max_length=50, blank=True, null=True)
    
    data = models.JSONField(default=dict)

    def __str__(self):
        return self.name
    
class Move(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    # Básico da Batalha
    type = models.CharField(max_length=50)       # normal, fire...
    category = models.CharField(max_length=50)   # physical, special, status
    power = models.IntegerField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)
    pp = models.IntegerField()
    
    # Estratégia Avançada (Elifoot mode)
    priority = models.IntegerField(default=0)    # Quem ataca primeiro?
    target = models.CharField(max_length=50)     # selected-pokemon, all-opponents...
    effect_chance = models.IntegerField(null=True, blank=True) # % de chance de queimar/congelar
    
    # A Descrição
    description = models.TextField(blank=True)
    
    # O Cérebro do Golpe (Meta Data)
    # Aqui vai: ailment (paralisia), crit_rate, drain, healing, flinch_chance...
    # Salvamos o JSON "meta" inteirinho aqui.
    mechanics = models.JSONField(default=dict) 

    def __str__(self):
        return f"{self.name} ({self.category}) - Pwr: {self.power or 0}"