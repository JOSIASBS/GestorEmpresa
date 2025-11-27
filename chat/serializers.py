from rest_framework import serializers
from users.models import User
from .models import ChatGroup, Message

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    recipient = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'group', 'content', 'timestamp']

class ChatGroupSerializer(serializers.ModelSerializer):
    miembros = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    mensajes = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'nombre', 'descripcion', 'miembros', 'mensajes', 'creado']
