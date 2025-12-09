from django.db import models
from django.conf import settings

class Evento(models.Model):
    TIPO_CHOICES = [
        ('tarea', 'Tarea'),
        ('reunion', 'Reunión'),
        ('otro', 'Otro'),
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"