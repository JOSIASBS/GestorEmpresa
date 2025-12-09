from rest_framework import viewsets, permissions
from .models import ChatGroup, Message
from .serializers import ChatGroupSerializer, MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from users.models import User

class ChatGroupViewSet(viewsets.ModelViewSet):
    queryset = ChatGroup.objects.all()
    serializer_class = ChatGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        group = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, group=group)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]


def chat_groups_list(request):
    grupos = ChatGroup.objects.filter(miembros=request.user)
    privados = []

    try:
        obtener_grupo_anuncios = ChatGroup.objects.get(nombre='Anuncios')
    except ChatGroup.DoesNotExist:
        obtener_grupo_anuncios = None

    return render(request, 'chat/chat_groups_list.html', {
        'grupos': grupos,
        'privados': privados,
        'empleado': request.user,
        'obtener_grupo_anuncios': obtener_grupo_anuncios,
    })


def chat_group_detail(request, pk):
    grupo = get_object_or_404(ChatGroup, pk=pk)
    mensajes = Message.objects.filter(group=grupo).order_by('timestamp')

    # Manejar envío de mensaje sin form
    if request.method == 'POST' and request.POST.get('content'):
        Message.objects.create(
            sender=request.user,
            group=grupo,
            content=request.POST.get('content')
        )
        return redirect('chat:chat_group_detail', pk=pk)

    puede_enviar = True
    return render(request, 'chat/chat_group_detail.html', {
        'grupo': grupo,
        'mensajes': mensajes,
        'puede_enviar': puede_enviar,
        'empleado': request.user
    })


def crear_chat(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        nombre = request.POST.get('nombre')
        miembros_ids = request.POST.getlist('miembros')
        grupo = ChatGroup.objects.create(nombre=nombre, tipo=tipo)
        grupo.miembros.set(User.objects.filter(id__in=miembros_ids))
        return redirect('chat:chat_groups_list')

    return render(request, 'chat/crear_chat.html')


def private_chat(request, pk):
    other = get_object_or_404(User, pk=pk)
    mensajes = Message.objects.filter(group__miembros__in=[request.user, other]).order_by('timestamp')

    if request.method == 'POST' and request.POST.get('content'):
        Message.objects.create(
            sender=request.user,
            group=None,
            content=request.POST.get('content')
        )
        return redirect('chat:private_chat', pk=pk)

    puede_enviar = True
    return render(request, 'chat/private_chat.html', {
        'other': other,
        'mensajes': mensajes,
        'puede_enviar': puede_enviar,
        'empleado': request.user
    })