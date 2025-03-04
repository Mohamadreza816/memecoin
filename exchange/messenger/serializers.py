from rest_framework import serializers
from messenger.models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['owner','username','to_add','text','file','created_at','m_status']
        extra_kwargs = {
            'owner': {'read_only': True},
            'username': {'read_only': True},
            'm_status': {'read_only': True},
            'created_at': {'read_only': True},
        }
