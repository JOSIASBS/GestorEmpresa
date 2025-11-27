from rest_framework import viewsets, permissions
from .models import ChatGroup, Message
from .serializers import ChatGroupSerializer, MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class ChatGroupViewSet(viewsets.ModelViewSet):
    queryset = ChatGroup.objects.all()
    serializer_class = ChatGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        group = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, group=group)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
