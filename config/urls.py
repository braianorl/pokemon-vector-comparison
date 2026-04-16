"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from re import search
from django.contrib import admin
from django.urls import path
from arena.views import get_pokemon_details, index, search_pokemon  # minha view importada

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'), # Rota vazia ('') significa Home Page
    path('search/', search_pokemon, name='search'), 
    path('api/pokemon/<int:id>/', get_pokemon_details, name='api_pokemon'),
]