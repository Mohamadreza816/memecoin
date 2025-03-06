from rest_framework import serializers
from .models import Transaction
from users.models import CustomUser
from market.models import Mycoin
from django.utils import timezone
class TransactionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=1)
    status = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    class Meta:
        model = Transaction
        fields = ['type','to_add','amount','time','status']
        read_only_fields = ['time','status']
        extra_kwargs = {
            'to_add': {'required': False},
        }

    def validate_amount(self, data):
        if data < 0 :
            raise serializers.ValidationError("amount cannot be less than zero")
        return data


    def validate_to_add(self, data):
        if data is None or data == '' or data is ...:
            return None
        if not CustomUser.objects.filter(address = data).exists():
            raise serializers.ValidationError("Destination Address does not exist")
        return data

    def get_status(self, obj):
        return obj.status

class TransactionFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    min_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    sender_name = serializers.CharField(required=False)
    receiver_name = serializers.CharField(required=False)



class walletaddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','address']
        read_only_fields = ['address','username']


class getnamepriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mycoin
        fields = ['name','price']