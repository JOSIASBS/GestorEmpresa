from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('fichar/', views.fichar, name='fichar'),
path('perfil/', views.perfil, name='perfil'),
path('perfil/editar/', views.perfil_editar, name='perfil_editar'),
path('perfil/cambiar-password/', views.perfil_cambiar_password, name='perfil_cambiar_password'),
path('chat/crear/', views.crear_chat, name='crear_chat'),
path('reportes/', views.reportes_asistencia, name='reportes_asistencia'),
path('calendario/', views.calendario, name='calendario'),
path('solicitudes/', views.solicitudes, name='solicitudes'),
path('solicitudes/<int:solicitud_id>/<str:accion>/', views.aprobar_solicitud, name='aprobar_solicitud'),

    path('departamentos/', views.departamentos_list, name='departamentos_list'),
    path('empleados/', views.empleados_list, name='empleados_list'),
    path('empleados/<int:empleado_id>/', views.empleado_detail, name='empleado_detail'),
    path('chat/', views.chat_groups_list, name='chat_groups_list'),
    path('chat/group/<int:group_id>/', views.chat_group_detail, name='chat_group_detail'),
    path('chat/private/<int:empleado_id>/', views.private_chat, name='private_chat'),
    path('accounts/', include('django.contrib.auth.urls')),
]
