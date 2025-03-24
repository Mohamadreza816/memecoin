from django.shortcuts import render
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView
from rest_framework import generics , permissions,status
from .serializers import UserSerializer,LoginSerializer,UserUpdateserializers,changePasswordSerializer
from .models import CustomUser
from logs.models import logs
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

# register new user
class Signup(generics.CreateAPIView):
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
        logs.objects.create(
            owner=user,
            action="Signup",
            logDetails="New user registered",
        )

class Login(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            user = CustomUser.objects.get(username=username)
            logs.objects.create(
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
            log = logs.objects.create(
                owner=self.request.user,
                action="Logout",
                logDetails=f"{request.user.username} Logged out",
            )
            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)


class checklogin(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": "User is authenticated", "user":request.user.username}, status=200)


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserUpdateserializers

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        if not request.data:
            return Response({"error": "Invalid request"}, status=400)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        log = logs.objects.create(
            owner=self.get_object(),
            action="Edit Profile",
            logDetails=f"{self.get_object().username} Profile",
        )
        return Response(serializer.data)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=changePasswordSerializer,
        responses={
            200: {
                "description": "Password changed successfully",
                "example": {
                    "message": "Your password has been changed successfully.",
                    "status": "success"
                }
            },
            400: {
                "description": "Invalid password format",
                "example": {
                    "message": "Old password is incorrect",
                    "status": "error"
                }
            }
        },        description="Filter transactions based on date range, amount, sender, and receiver",
        summary="Filter Transactions"
    )
    def put(self, request, *args, **kwargs):
        serializer = changePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.update_password()
        log = logs.objects.create(
            owner=self.request.user,
            action="Change Password",
            logDetails=f"{self.request.user.username} changed Password",
        )
        return Response({"message": "Password updated successfully"}, status=200)