from django.db import models
from django.contrib.auth.models import User

class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Posicion(models.Model):

    cargo = models.CharField(max_length=100)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='posiciones'
    )


    def __str__(self):
        return self.cargo

class Empleado(models.Model):
    ROLE_CHOICES = (
    ('empleado', 'Empleado'),
    ('manager', 'Manager'),
    ('admin', 'Administrador'),
    )
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)
    posicion = models.ForeignKey(Posicion, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_contratacion = models.DateField(auto_now_add=True)
    foto = models.ImageField(upload_to='fotos_empleados/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='empleado')

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Fichaje(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='fichajes')
    hora_entrada = models.DateTimeField(null=True, blank=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empleado.user.username} - {self.fecha}"
    class Meta:
        ordering = ['-fecha', '-hora_entrada']


class ChatGroup(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    miembros = models.ManyToManyField(Empleado, related_name='grupos')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Message(models.Model):
    sender = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='mensajes_enviados')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='mensajes')
    recipient = models.ForeignKey(Empleado, on_delete=models.CASCADE, null=True, blank=True, related_name='mensajes_recibidos')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        if self.group:
            return f"{self.sender.user.username} -> grupo {self.group.nombre}: {self.content[:30]}"
        if self.recipient:
            return f"{self.sender.user.username} -> {self.recipient.user.username}: {self.content[:30]}"
        return f"{self.sender.user.username}: {self.content[:30]}"


class Evento(models.Model):
    TIPO_CHOICES = (
        ('reunion', 'Reunión'),
        ('tarea', 'Tarea'),
        ('otro', 'Otro'),
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    creador = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='eventos_creados')
    asignados = models.ManyToManyField(Empleado, related_name='eventos_asignados', blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio.date()})"


class Solicitud(models.Model):

    TIPO_SOLICITUD = (
        ('vacaciones', 'Vacaciones'),
        ('permiso', 'Permiso'),
        ('ausencia', 'Ausencia'),
    )

    ESTADO_SOLICITUD = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    )

    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_SOLICITUD)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    motivo = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_SOLICITUD, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empleado.user.username} - {self.tipo} ({self.estado})"