from django.db import models
from django.conf import settings

class ChatGroup(models.Model):
    nombre = models.CharField(max_length=255, db_column='nombre')
    descripcion = models.TextField(blank=True, null=True, db_column='descripcion')
    tipo = models.CharField(max_length=50, default='grupal', db_column='tipo')
    creado = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChatGroupMiembros',  # Indica la tabla intermedia
        related_name='chat_groups'
    )

    class Meta:
        db_table = 'chat_group'


class ChatGroupMiembros(models.Model):
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, db_column='chat_group_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'chat_group_miembros'
        unique_together = ('chat_group', 'user')


class Message(models.Model):
    group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name='mensajes',
        db_column='chat_group_id'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        db_column='sender_id'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_recibidos',
        null=True,
        blank=True,
        db_column='recipient_id'
    )
    content = models.TextField(db_column='content')
    timestamp = models.DateTimeField(auto_now_add=True, db_column='timestamp')

    class Meta:
        db_table = 'message'


class MessageFile(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        db_column='message_id',
        related_name='archivos'
    )
    archivo = models.CharField(max_length=255, db_column='archivo')

    class Meta:
        db_table = 'message_file'