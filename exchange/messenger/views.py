from rest_framework import status,generics,permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Message
from users.models import CustomUser
from .serializers import MessageSerializer
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.

class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permissions_classes = [permissions.IsAuthenticated]
    # parser_classes = (MultiPartParser, FormParser)
    def perform_create(self, serializer):
        to_address = self.request.data.get("to_add")
        if not CustomUser.objects.filter(address=to_address).exists():
            raise ValidationError({"error": "Receiver wallet address is invalid."})

        serializer.save(owner=self.request.user,username=self.request.user.username,m_status='US')

class UserMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    # parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Message.objects.filter(to_add=self.request.user.address).order_by('-created_at')

