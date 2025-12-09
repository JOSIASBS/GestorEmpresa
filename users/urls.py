from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('', views.login_page, name='home'),
    path('fichar/', views.fichar_page, name='fichar'),
    path('perfil/', views.perfil_page, name='perfil'),
    path('empleados/', views.empleados_list, name='empleados_list'),
    path('solicitudes/', views.solicitudes_list, name='solicitudes_list'),
    path('reportes/', views.reportes_list, name='reportes_list'),
    path('perfil/editar/', views.perfil_page, name='perfil_editar'),
    path('departamentos/', views.departamento_list, name='departamento_list'),
]
