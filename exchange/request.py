import requests

endpoint = "http://127.0.0.1:8000/"
# ?abc=12500"

# get_response = requests.get(endpoint)
get_response = requests.post(endpoint,json={"title":"yoho"})

print(get_response.json())


# import requests
#
# endpoint = "http://127.0.0.1:8000/"
#
# access_token = "YOUR_ACCESS_TOKEN_HERE"
#

# headers = {
#     'Authorization': f'Bearer {access_token}'
# }
#
# #
# get_response = requests.post(endpoint, json={"title": "yoho"}, headers=headers)
#
# print(get_response.json())


{
	"username":"samin",
  	"password" : "45"
}

{
  "type":"B",
  "amount":100

}
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Transaction
from users.models import CustomUser
from .serializers import TransactionSerializer, TransactionFilterSerializer
from django.db.models import Q

class TransactionFilter(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=TransactionFilterSerializer,  # ورودی API
        responses=TransactionSerializer(many=True),  # خروجی API
        description="Filter transactions based on date range, amount, sender, and receiver",
        summary="Filter Transactions"
    )
    def post(self, request):
        filter_serialize = TransactionFilterSerializer(data=request.data)
        filter_serialize.is_valid(raise_exception=True)
        queryset = Transaction.objects.filter(owner=request.user)
        filters = filter_serialize.validated_data

        if not any(filters.values()):
            raise ValidationError({"Error": "At least one filter must be specified."})

        start_date = filters.get('start_date', None)
        end_date = filters.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(time__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(time__gte=start_date)
        elif end_date:
            queryset = queryset.filter(time__lte=end_date)

        min_amount = filters.get('min_amount', None)
        max_amount = filters.get('max_amount', None)
        if min_amount is not None:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount is not None:
            queryset = queryset.filter(amount__lte=max_amount)

        sender_name = filters.get('sender_name', None)
        if sender_name:
            queryset = queryset.filter(owner__username__icontains=sender_name)

        receiver_name = filters.get('receiver_name', None)
        if receiver_name:
            try:
                receiver_address = CustomUser.objects.get(username=receiver_name)
                queryset = queryset.filter(to_add=receiver_address.address)
            except CustomUser.DoesNotExist:
                raise ValidationError({"Error": "Receiver with this username does not exist"})

        if not queryset.exists():
            return Response({"Error": "No transactions found."}, status=status.HTTP_404_NOT_FOUND)

        result = TransactionSerializer(queryset, many=True)
        return Response(result.data, status=status.HTTP_200_OK)


from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import Transaction
from .serializers import TransactionSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class BalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get user balance",
        description="Returns the balance and memecoin balance of the authenticated user.",
        responses={200: {"balance": int, "memecoin_balance": int}}
    )
    def get(self, request):
        try:
            balance = request.user.balance
            memecoin_balance = request.user.memecoin_balance
            return Response({"balance": balance, "memecoin_balance": memecoin_balance}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Deposit money",
        description="Allows users to deposit money into their balance. Balance must be greater than 0.",
        request={"type": "object", "properties": {"balance": {"type": "integer"}}},
        responses={200: {"new_balance": int}, 400: {"Error": "balance cannot be empty"}}
    )
    def post(self, request):
        balance = request.data.get("balance")
        user = request.user
        if balance is None or balance <= 0:
            Transaction.objects.create(
                owner=user,
                type=Transaction.Type.Deposit,
                amount=0,
                status=Transaction.Status.Failed,
            )
            return Response({"Error": "balance cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        user.balance += balance
        user.save()
        request.user.refresh_from_db()
        Transaction.objects.create(
            owner=user,
            type=Transaction.Type.Deposit,
            amount=balance,
            status=Transaction.Status.Complete,
        )
        return Response({"new_balance": user.balance}, status=status.HTTP_200_OK)
