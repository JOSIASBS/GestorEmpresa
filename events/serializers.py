from rest_framework import serializers
from .models import Evento

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'titulo', 'descripcion', 'tipo', 'fecha_inicio', 'fecha_fin', 'creado_por']