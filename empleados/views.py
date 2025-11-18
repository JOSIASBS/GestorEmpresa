from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django import forms
from django.db.models import Q
from django.contrib import messages
from datetime import timedelta, datetime, time
from .models import Empleado, Fichaje, Departamento, ChatGroup, Message, Evento, Solicitud
from .forms import MessageForm, PerfilForm, EventoForm, CrearChatForm, SolicitudForm
import calendar



def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('fichar')
        else:
            messages.error(request,"Usuario o contraseña incorrectos.")

    return render(request, 'empleados/login.html')

@login_required
def empleados_list(request):
    usuario = request.user
    empleado = Empleado.objects.get(user=usuario)


    nombre = request.GET.get('nombre', '')
    fecha = request.GET.get('fecha', '')
    departamento_id = request.GET.get('departamento', '')


    if empleado.role == 'admin':
        empleados = Empleado.objects.select_related('user', 'posicion__departamento').all()
    elif empleado.role == 'manager':
        if empleado.posicion and empleado.posicion.departamento:
            empleados = Empleado.objects.filter(posicion__departamento=empleado.posicion.departamento)
        else:
            empleados = Empleado.objects.none()
    else:
        messages.error(request, "No tienes permiso para ver esta página.")
        return redirect('fichar')


    if nombre:
        empleados = empleados.filter(
            Q(user__first_name__icontains=nombre) |
            Q(user__last_name__icontains=nombre) |
            Q(user__username__icontains=nombre)
        )

    if fecha:
        empleados = empleados.filter(fecha_contratacion=fecha)

    if empleado.role == 'admin' and departamento_id:
        empleados = empleados.filter(posicion__departamento__id=departamento_id)


    departamentos = Departamento.objects.all() if empleado.role == 'admin' else None

    return render(request, 'empleados/empleados_list.html', {
        'empleados': empleados,
        'departamentos': departamentos,
        'is_admin': empleado.role == 'admin'
    })


@login_required
def fichar(request):
    empleado, created = Empleado.objects.get_or_create(user=request.user)
    hoy = timezone.now().date()
    fichaje_hoy = Fichaje.objects.filter(empleado=empleado, fecha__date=hoy, hora_salida__isnull=True).first()

    if request.method == "POST":
        if 'entrada' in request.POST:
            if not fichaje_hoy:
                Fichaje.objects.create(empleado=empleado, hora_entrada=timezone.now())
        elif 'salida' in request.POST and fichaje_hoy:
            fichaje_hoy.hora_salida = timezone.now()
            fichaje_hoy.save()
        return redirect('fichar')

    fichajes = Fichaje.objects.filter(empleado=empleado)[:10]
    return render(request, 'empleados/fichar.html', {
        'empleado': empleado,
        'fichaje_hoy': fichaje_hoy,
        'fichajes': fichajes,
    })

@login_required
def perfil(request):
    empleado, _ = Empleado.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil')
    else:
        form = PerfilForm(instance=empleado)
    return render(request, 'empleados/perfil.html', {'form': form})


@login_required
def departamentos_list(request):
    empleado = Empleado.objects.get(user=request.user)


    if empleado.role == 'admin':
        departamentos = Departamento.objects.all()
        data = []
        for dep in departamentos:
            empleados_dep = Empleado.objects.filter(posicion__departamento=dep)
            data.append({
                'departamento': dep,
                'total_empleados': empleados_dep.count(),
            })
        return render(request, 'empleados/departamentos_admin.html', {'data': data})


    elif empleado.role == 'manager':
        if empleado.posicion and empleado.posicion.departamento:
            dep = empleado.posicion.departamento
            empleados_dep = Empleado.objects.filter(posicion__departamento=dep)
            ahora = timezone.now()
            conectados = empleados_dep.filter(
                user__last_login__gte=ahora - timedelta(minutes=10)
            ).count()

            return render(request, 'empleados/departamentos_manager.html', {
                'departamento': dep,
                'empleados': empleados_dep,
                'total_empleados': empleados_dep.count(),
                'conectados': conectados,
            })
        else:
            messages.warning(request, "No estás asignado a ningún departamento.")
            return redirect('fichar')



    else:

        messages.error(request, "No tienes permiso para acceder a los departamentos.")

        return redirect('fichar')
'''
@login_required
def empleados_list(request):
    empleados = Empleado.objects.select_related('user', 'posicion').all()
    return render(request, 'empleados/empleados_list.html', {'empleados': empleados})
'''
@login_required
def empleado_detail(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    fichajes = empleado.fichajes.all()[:20]
    return render(request, 'empleados/empleado_detail.html', {'empleado': empleado, 'fichajes': fichajes})

@login_required
def chat_groups_list(request):
    empleado, _ = Empleado.objects.get_or_create(user=request.user)

    # Chats grupales donde es miembro
    grupos = ChatGroup.objects.filter(miembros=empleado)

    # Chats privados
    privados_ids = Message.objects.filter(
        Q(sender=empleado) | Q(recipient=empleado),
        group__isnull=True
    ).values_list('sender', 'recipient')

    privados_ids_flat = set()
    for sid, rid in privados_ids:
        if sid != empleado.id:
            privados_ids_flat.add(sid)
        if rid != empleado.id:
            privados_ids_flat.add(rid)

    privados = Empleado.objects.filter(id__in=privados_ids_flat)

    # --- Aseguramos que exista el chat de Anuncios ---
    grupo_anuncios, created = ChatGroup.objects.get_or_create(nombre='Anuncios', defaults={'descripcion': 'Noticias internas'})
    if created:
        # Añadir a todos los empleados
        grupo_anuncios.miembros.set(Empleado.objects.all())
    else:
        # Asegurarse que todos los empleados estén en el grupo
        todos = Empleado.objects.all()
        grupo_anuncios.miembros.set(todos)

    return render(request, 'empleados/chat_groups_list.html', {
        'empleado': empleado,
        'grupos': grupos,
        'privados': privados,
        'obtener_grupo_anuncios': grupo_anuncios,
    })

@login_required
def crear_chat(request):
    empleado = Empleado.objects.get(user=request.user)
    form = CrearChatForm()


    if empleado.role == 'admin':
        form.fields['miembros'].queryset = Empleado.objects.exclude(id=empleado.id)

    elif empleado.role == 'manager':
        if empleado.posicion and empleado.posicion.departamento:
            form.fields['miembros'].queryset = Empleado.objects.filter(
                posicion__departamento=empleado.posicion.departamento
            ).exclude(id=empleado.id)
        else:
            messages.warning(request, "No tienes departamento asignado.")
            return redirect('chat_groups_list')

    elif empleado.role == 'empleado':
        if empleado.posicion and empleado.posicion.departamento:
            form.fields['miembros'].queryset = Empleado.objects.filter(
                posicion__departamento=empleado.posicion.departamento
            ).exclude(id=empleado.id)
        else:
            messages.warning(request, "No tienes departamento asignado.")
            return redirect('chat_groups_list')

        # El empleado no puede crear grupos, solo privados
        form.fields['tipo'].choices = [('privado', 'Privado')]


    if request.method == 'POST':
        form = CrearChatForm(request.POST)
        form.fields['miembros'].queryset = Empleado.objects.all()  # Rellenar de nuevo

        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            miembros = form.cleaned_data['miembros']

            if tipo == 'grupo':
                if empleado.role == 'empleado':
                    messages.error(request, "No tienes permiso para crear grupos.")
                    return redirect('chat_groups_list')

                nombre = form.cleaned_data['nombre'] or f"Grupo de {empleado.user.username}"
                grupo = ChatGroup.objects.create(nombre=nombre, descripcion=f"Creado por {empleado.user.username}")
                grupo.miembros.add(empleado, *miembros)
                messages.success(request, f"Grupo '{nombre}' creado correctamente.")
                return redirect('chat_group_detail', group_id=grupo.id)

            elif tipo == 'privado':
                if len(miembros) != 1:
                    messages.error(request, "Selecciona solo un miembro para chat privado.")
                else:
                    other = miembros.first()
                    # Redirigir al chat privado existente o nuevo
                    return redirect('private_chat', empleado_id=other.id)

    return render(request, 'empleados/crear_chat.html', {'form': form})

@login_required
def chat_group_detail(request, group_id):
    empleado, _ = Empleado.objects.get_or_create(user=request.user)
    grupo = get_object_or_404(ChatGroup, pk=group_id)

    # Asegurarse que el usuario sea miembro
    if not grupo.miembros.filter(pk=empleado.pk).exists():
        grupo.miembros.add(empleado)

    # Solo admin y manager pueden publicar en Anuncios
    if grupo.nombre == "Anuncios" and empleado.role == "empleado":
        puede_enviar = False
    else:
        puede_enviar = True

    if request.method == 'POST' and puede_enviar:
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(sender=empleado, group=grupo, content=form.cleaned_data['content'])
            return redirect('chat_group_detail', group_id=group_id)
    else:
        form = MessageForm() if puede_enviar else None

    mensajes = grupo.mensajes.select_related('sender').all()
    return render(request, 'empleados/chat_group_detail.html', {
        'grupo': grupo,
        'mensajes': mensajes,
        'form': form,
        'puede_enviar': puede_enviar
    })


def obtener_grupo_anuncios():
    grupo, created = ChatGroup.objects.get_or_create(nombre='Anuncios')

    todos = Empleado.objects.all()
    grupo.miembros.set(todos)
    grupo.save()
    return grupo

@login_required
def private_chat(request, empleado_id):
    me, _ = Empleado.objects.get_or_create(user=request.user)
    other = get_object_or_404(Empleado, pk=empleado_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(sender=me, recipient=other, content=form.cleaned_data['content'])
            return redirect('private_chat', empleado_id=empleado_id)
    else:
        form = MessageForm()

    mensajes = Message.objects.filter(group__isnull=True).filter(
        Q(sender=me, recipient=other) | Q(sender=other, recipient=me)
    ).select_related('sender', 'recipient').all()

    return render(request, 'empleados/private_chat.html', {'other': other, 'mensajes': mensajes, 'form': form})

@login_required
def reportes_asistencia(request):
    empleado, _ = Empleado.objects.get_or_create(user=request.user)

    if empleado.role not in ['admin', 'manager']:
        messages.error(request, "No tienes permiso para ver los reportes.")
        return redirect('fichar')

    hoy = timezone.now()
    mes = int(request.GET.get('mes', hoy.month))
    año = int(request.GET.get('año', hoy.year))

    primer_dia = datetime(año, mes, 1)
    ultimo_dia = datetime(año, mes, calendar.monthrange(año, mes)[1])


    if empleado.role == 'admin':
        empleados = Empleado.objects.all()
    elif empleado.role == 'manager':
        if empleado.posicion and empleado.posicion.departamento:
            empleados = Empleado.objects.filter(posicion__departamento=empleado.posicion.departamento)
        else:
            empleados = Empleado.objects.none()


    nombre = request.GET.get('nombre')
    if nombre:
        empleados = empleados.filter(
            Q(user__first_name__icontains=nombre) |
            Q(user__last_name__icontains=nombre) |
            Q(user__username__icontains=nombre)
        )

    reportes = []

    for e in empleados:
        fichajes_mes = Fichaje.objects.filter(
            empleado=e,
            fecha__date__gte=primer_dia,
            fecha__date__lte=ultimo_dia
        ).order_by('fecha')

        total_horas = 0
        retrasos = 0
        dias_trabajados = set()
        dias_faltas = []

        for f in fichajes_mes:
            if f.hora_entrada and f.hora_salida:
                dias_trabajados.add(f.fecha.date())
                delta = f.hora_salida - f.hora_entrada
                total_horas += delta.total_seconds() / 3600

                if f.hora_entrada.time() > time(7, 5):
                    retrasos += 1

        for d in range(calendar.monthrange(año, mes)[1]):
            dia = datetime(año, mes, d + 1)
            if dia.weekday() < 5:
                if dia.date() not in dias_trabajados:
                    dias_faltas.append(dia.date())

        reportes.append({
            'empleado': e,
            'total_horas': total_horas,
            'retrasos': retrasos,
            'dias_trabajados': len(dias_trabajados),
            'dias_faltas': dias_faltas,
        })

    return render(request, 'empleados/reportes_asistencia.html', {
        'reportes': reportes,
        'mes': mes,
        'año': año,
        'nombre': nombre or ''
    })

@login_required
def calendario(request):
    empleado, _ = Empleado.objects.get_or_create(user=request.user)

    # Manejar eliminación
    if request.method == 'POST' and 'eliminar_id' in request.POST:
        if empleado.role in ['admin', 'manager']:
            Evento.objects.filter(id=request.POST['eliminar_id']).delete()

        else:
            messages.error(request, "No tienes permisos para eliminar eventos.")
        return redirect('calendario')

    # Filtrado de eventos
    if empleado.role == 'admin':
        eventos = Evento.objects.all()
    elif empleado.role == 'manager':
        if empleado.posicion and empleado.posicion.departamento:
            eventos = Evento.objects.filter(
                Q(creador=empleado) | Q(asignados__in=[empleado])
            ).distinct()
        else:
            eventos = Evento.objects.none()
    else:
        eventos = Evento.objects.filter(Q(asignados=empleado) | Q(creador=empleado)).distinct()

    # Crear evento
    if request.method == 'POST' and 'eliminar_id' not in request.POST:
        if empleado.role in ['admin', 'manager']:
            form = EventoForm(request.POST, empleado=empleado)
            if form.is_valid():
                evento = form.save(commit=False)
                evento.creador = empleado
                evento.save()
                form.save_m2m()

                return redirect('calendario')
        else:
            messages.error(request, "No tienes permisos para crear eventos.")
            return redirect('calendario')
    else:
        form = EventoForm(empleado=empleado) if empleado.role in ['admin', 'manager'] else None

    return render(request, 'empleados/calendario.html', {
        'eventos': eventos,
        'form': form,
        'empleado': empleado
    })

@login_required
def solicitudes(request):
    empleado, _ = Empleado.objects.get_or_create(user=request.user)

    # Crear nueva solicitud
    if request.method == 'POST' and 'crear' in request.POST:
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.empleado = empleado
            solicitud.save()
            messages.success(request, "Solicitud enviada correctamente.")
            return redirect('solicitudes')
    else:
        form = SolicitudForm()

    # Listado de solicitudes visibles
    if empleado.role in ['admin', 'manager']:
        solicitudes = Solicitud.objects.all().order_by('-creado_en')
    else:
        solicitudes = Solicitud.objects.filter(empleado=empleado).order_by('-creado_en')

    context = {
        'form': form,
        'solicitudes': solicitudes,
        'empleado': empleado
    }
    return render(request, 'empleados/solicitudes.html', context)


@login_required
def aprobar_solicitud(request, solicitud_id, accion):
    empleado, _ = Empleado.objects.get_or_create(user=request.user)
    if empleado.role not in ['admin', 'manager']:
        messages.error(request, "No tienes permisos para aprobar solicitudes.")
        return redirect('solicitudes')

    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if accion == 'aprobar':
        solicitud.estado = 'aprobada'
    elif accion == 'rechazar':
        solicitud.estado = 'rechazada'
    solicitud.save()
    messages.success(request, f"Solicitud {accion} correctamente.")
    return redirect('solicitudes')


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['telefono', 'direccion', 'fecha_ingreso', 'posicion', 'foto']


class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(widget=forms.PasswordInput)
    nueva_password = forms.CharField(widget=forms.PasswordInput)
    confirmar_password = forms.CharField(widget=forms.PasswordInput)


@login_required
def perfil(request):
    empleado = Empleado.objects.get(user=request.user)
    return render(request, 'empleados/perfil.html', {'empleado': empleado})


@login_required
def perfil_editar(request):
    empleado = Empleado.objects.get(user=request.user)

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil')
    else:
        form = EditarPerfilForm(instance=empleado)

    return render(request, 'empleados/perfil_editar.html', {'form': form, 'empleado': empleado})


@login_required
def perfil_cambiar_password(request):
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            user = request.user

            if not user.check_password(form.cleaned_data['password_actual']):
                messages.error(request, "La contraseña actual no es correcta.")
            elif form.cleaned_data['nueva_password'] != form.cleaned_data['confirmar_password']:
                messages.error(request, "Las contraseñas nuevas no coinciden.")
            else:
                user.set_password(form.cleaned_data['nueva_password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña cambiada correctamente.")
                return redirect('perfil')
    else:
        form = CambiarPasswordForm()

    return render(request, 'empleados/perfil_cambiar_password.html', {'form': form})