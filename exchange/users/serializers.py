from rest_framework import serializers
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username','password', 'email','balance', 'date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user