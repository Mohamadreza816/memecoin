from django.urls import path
from transactions.views import TransactionView

urlpatterns = [
    path('transactions/', TransactionView.as_view(), name='transactions'),
]