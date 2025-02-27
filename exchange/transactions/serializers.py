from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Transaction
        fields = '__all__'
