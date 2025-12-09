from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'chat'

router = DefaultRouter()
router.register(r'groups', views.ChatGroupViewSet, basename='chatgroup')
router.register(r'messages', views.MessageViewSet, basename='message')

urlpatterns = [

    path('api/', include(router.urls)),


    path('', views.chat_groups_list, name='chat_groups_list'),
    path('crear/', views.crear_chat, name='crear_chat'),
    path('grupo/<int:pk>/', views.chat_group_detail, name='chat_group_detail'),
    path('privado/<int:pk>/', views.private_chat, name='private_chat'),

]
