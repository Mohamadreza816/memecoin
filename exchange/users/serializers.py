from django.utils.timezone import localtime
import pytz
from rest_framework import serializers
from users.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id','first_name','last_name', 'username' ,'password','confirm_password', 'email','balance', 'date_joined']

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError({'error' : 'Passwords must match'})
        return data
    #     # validate_password(password)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        conf_password = validated_data.pop('confirm_password', None)
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_date_joined(self, obj):
        iran_tz = pytz.timezone("Asia/Tehran")
        local_time = localtime(obj.date_joined, iran_tz)
        return local_time.strftime("%Y-%m-%d ---- %H:%M:%S")
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
