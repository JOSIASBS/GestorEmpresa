from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User, Fichaje
from django.utils import timezone

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("users:fichar")
        else:
            return render(request, "users/login.html", {"error": "Usuario o contraseña incorrectos"})

    return render(request, 'users/login.html')


@login_required
def fichar_page(request):
    empleado = request.user
    hoy = timezone.localdate()


    fichaje = Fichaje.objects.filter(empleado=empleado, fecha=hoy).first()

    if request.method == 'POST':

        if 'entrada' in request.POST:
            if fichaje is None:

                fichaje = Fichaje.objects.create(
                    empleado=empleado,
                    fecha=hoy,
                    hora_entrada=timezone.localtime().time()
                )
            elif fichaje.hora_entrada is None:

                fichaje.hora_entrada = timezone.localtime().time()
                fichaje.save()


        elif 'salida' in request.POST:
            if fichaje and fichaje.hora_salida is None:
                fichaje.hora_salida = timezone.localtime().time()
                fichaje.save()

        return redirect('users:fichar')


    fichajes = empleado.fichajes.all()

    return render(request, 'users/fichar.html', {
        'empleado': empleado,
        'fichaje_hoy': fichaje,
        'fichajes': fichajes,
    })



@login_required
def empleados_list(request):
    if request.user.role not in ['manager', 'admin']:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    empleados = User.objects.filter(role='employee')
    return render(request, 'users/empleados_list.html', {'empleados': empleados})

@login_required
def perfil_page(request):
    empleado = request.user
    return render(request, "users/perfil.html", {"empleado": empleado})

@login_required
def solicitudes_list(request):
    return render(request, "users/Solicitudes.html")

@login_required
def reportes_list(request):
    return render(request, "users/reportes_asistencia.html")

@login_required
def perfil_editar(request):

    return render(request, "users/perfil_editar.html")

@login_required
def departamento_list(request):

    return render(request, "users/departamentos_list.html")