from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics , permissions
from .serializers import UserSerializer
from .models import CustomUser
# Create your views here.

# register new user
class Signup(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

