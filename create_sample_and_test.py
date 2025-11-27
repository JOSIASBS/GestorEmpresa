import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','api.settings')
import django
django.setup()
from django.contrib.auth.models import User
from empleados.models import Departamento, Posicion, Empleado, ChatGroup, Message

# Crear usuarios
admin_user, created = User.objects.get_or_create(username='admin', defaults={'email':'admin@example.com'})
# Asegurar que el admin tenga una contraseña conocida y permisos (resetea si ya existía)
admin_user.set_password('adminpass')
admin_user.is_superuser = True
admin_user.is_staff = True
admin_user.save()

user2, created2 = User.objects.get_or_create(username='user2', defaults={'email':'user2@example.com'})
# Asegurar contraseña para user2 también (útil en pruebas)
user2.set_password('user2pass')
user2.save()

# Crear departamento y posición
dep, _ = Departamento.objects.get_or_create(nombre='IT', defaults={'descripcion':'Departamento de IT'})
pos, _ = Posicion.objects.get_or_create(cargo='Developer', departamento=dep)

# Crear empleados vinculados
emp_admin, _ = Empleado.objects.get_or_create(user=admin_user, defaults={'posicion': pos})
emp_user2, _ = Empleado.objects.get_or_create(user=user2, defaults={'posicion': pos})

# Crear grupo de chat y añadir miembros
group, gcreated = ChatGroup.objects.get_or_create(nombre='Equipo IT', defaults={'descripcion':'Grupo de IT'})
if gcreated or not group.miembros.filter(pk=emp_admin.pk).exists():
    group.miembros.add(emp_admin)
if not group.miembros.filter(pk=emp_user2.pk).exists():
    group.miembros.add(emp_user2)

# Crear un mensaje de ejemplo
if not Message.objects.filter(sender=emp_admin, group=group).exists():
    Message.objects.create(sender=emp_admin, group=group, content='Hola equipo, bienvenidos al chat!')

print('Sample data created:')
print(' admin:', admin_user.username)
print(' user2:', user2.username)
print(' departamento:', dep.nombre)
print(' posicion:', pos.cargo)
print(' empleados:', Empleado.objects.count())
print(' grupo:', group.nombre, ' miembros:', group.miembros.count())

# Probar rutas con cliente de pruebas
from django.test import Client
c = Client()
login_ok = c.login(username='admin', password='adminpass')
print('login ok (admin):', login_ok)

paths = ['/', '/departamentos/', '/empleados/', f'/chat/', f'/chat/group/{group.id}/', f'/chat/private/{emp_user2.id}/']
for p in paths:
    r = c.get(p)
    print(p, r.status_code, 'len', len(r.content))
    snippet = r.content.decode('utf-8', errors='replace')[:300]
    print(' snippet:', snippet.replace('\n',' ')[:200])
