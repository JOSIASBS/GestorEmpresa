import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','DjangoProject.settings')
import django
django.setup()
from django.db import connection
print('DATABASE:', connection.settings_dict.get('NAME'))
cur = connection.cursor()
cur.execute("SELECT name, applied FROM django_migrations WHERE app='empleados'")
mig = cur.fetchall()
print('migrations for empleados:', mig)

from django.test import Client
c = Client()
ok = c.login(username='admin', password='adminpass')
print('login ok?', ok)
r = c.get('/')
print('status', r.status_code)
print('\nresponse snippet:\n', r.content.decode('utf-8')[:800])

from empleados.models import Empleado
print('Empleados count:', Empleado.objects.count())

