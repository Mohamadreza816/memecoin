from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics , permissions,status
from .serializers import UserSerializer,LoginSerializer
from .models import CustomUser
from logs.models import logs
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

# register new user
class Signup(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    def create(self, request):
        response = super().create(request)
        user = self.get_queryset().get(id=response.data['id'])
    #     generate tokens
        refresh = RefreshToken.for_user(user)
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)
        return response
    def perform_create(self, serializer):
        user = serializer.save()
        last = logs.objects.create(
            owner=user,
            action="Signup",
            logDetails="New user registered",
        )
        print(last)
class Login(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            user = CustomUser.objects.get(username=username)
            last = logs.objects.create(
                owner=user,
                action="Login",
                logDetails=f"{user.username} Logged in",
            )
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)
