# productos/urls.py
"""URLs de la app productos — W02."""
from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='inicio'),
]