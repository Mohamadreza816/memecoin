from rest_framework import serializers
from .models import Transaction
from users.models import CustomUser
class TransactionSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(source='get_type')
    status = serializers.SerializerMethodField(source='get_status')
    class Meta:
        model = Transaction
        fields = ['type','from_add','to_add','amount','time','status']
        read_only_fields = ['time','status']


    def validate_amount(self, data):
        if data < 0 :
            raise serializers.ValidationError("amount cannot be less than zero")
        return data

    def validate_from_add(self, data):
        if not CustomUser.objects.filter(address = data).exists():
            raise serializers.ValidationError("Source Address does not exist")
        return data

    def validate_to_add(self, data):
        if not CustomUser.objects.filter(address = data).exists():
            raise serializers.ValidationError("Destination Address does not exist")
        return data
