from django.urls import path
from messenger.views import SendMessageView,UserMessagesView
urlpatterns = [
    path('sendmessege/', SendMessageView.as_view(), name='sendMessage'),
    path('readmesseges/', UserMessagesView.as_view(), name='UserMessages'),
]