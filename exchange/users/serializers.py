from django.utils.timezone import localtime
import pytz
from rest_framework import serializers
from users.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

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

class UserUpdateserializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name', 'username', 'email']

class changePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
          raise serializers.ValidationError({'error' : 'Invalid old password'})
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'error' : 'Passwords must match'})
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return data

    def update_password(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user