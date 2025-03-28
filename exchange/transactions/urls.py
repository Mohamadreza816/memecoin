from django.urls import path
from transactions.views import TransactionView,getAddbalance,TransactionList,Transactionfilter,WalletAddressView,getcoin

urlpatterns = [
    path('transactions/', TransactionView.as_view(), name='transactions'),
    path('getaddbalance/', getAddbalance.as_view(), name='getbalance'),
    path('transactionlist/', TransactionList.as_view(), name='TransactionList'),
    path('transactionfilter/', Transactionfilter.as_view(), name='Transactionfilter'),
    path('getwalletaddress/', WalletAddressView.as_view(), name='wallet-address'),
    path('getcoin/', getcoin.as_view(), name='coin'),
]