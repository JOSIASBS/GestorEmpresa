from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet, calendario

router = DefaultRouter()
router.register(r'eventos', EventoViewSet, basename='evento')

urlpatterns = [
    path('', calendario, name='calendario'),
    path('api/', include(router.urls)),
]