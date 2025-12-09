from rest_framework import viewsets, permissions
from .models import Evento
from .serializers import EventoSerializer
from django.shortcuts import render

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all().order_by('fecha_inicio')
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

def calendario(request):
    eventos = Evento.objects.all()
    return render(request, 'calendario/calendario.html', {'eventos': eventos, 'empleado': request.user})