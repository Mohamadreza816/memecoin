from django.contrib import admin
from django.urls import path
from .views import Signup, Login, Logout,checklogin,ProfileUpdateView,ChangePasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',Signup.as_view(),name='register'),
    path('login/',Login.as_view(),name='login'),
    path('logout/',Logout.as_view(),name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("checklogin/",checklogin.as_view(),name='checklogin'),
    path("profile/update/",ProfileUpdateView.as_view(),name='profile'),
    path("changepassword/",ChangePasswordView.as_view(),name='changepassword'),
]



