import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','DjangoProject.settings')
import django
django.setup()
import glob
from pathlib import Path
from django.db import connection

print('MIGRATION FILES:')
for p in sorted(Path('empleados/migrations').glob('*.py')):
    print(' -', p.name)

print('\nDJANGO_MIGRATIONS rows for app empleados:')
with connection.cursor() as cur:
    cur.execute("SELECT name, applied FROM django_migrations WHERE app='empleados'")
    rows = cur.fetchall()
    for r in rows:
        print(' -', r)

print('\nSQLITE tables starting with empleados_:')
with connection.cursor() as cur:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'empleados_%';")
    tables = cur.fetchall()
    for t in tables:
        print(' -', t[0])

print('\nAll tables count:')
with connection.cursor() as cur:
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
    print(cur.fetchone())

