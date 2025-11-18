from django.contrib import admin
from .models import Departamento, Posicion, Empleado, Fichaje, ChatGroup, Message

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')


@admin.register(Posicion)
class PosicionAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'departamento')


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('user', 'posicion', 'fecha_contratacion', 'activo')

@admin.register(Fichaje)
class FichajeAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'fecha', 'hora_entrada', 'hora_salida')
    list_filter = ('fecha', 'empleado')

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado')
    filter_horizontal = ('miembros',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'timestamp', 'group', 'recipient')
    list_filter = ('group', 'recipient', 'sender')
    search_fields = ('content',)
