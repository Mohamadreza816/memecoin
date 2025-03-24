from django.template.defaultfilters import first
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiTypes
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import generics , permissions,status
from rest_framework.views import APIView
from django.db.models import Q, DecimalField
from unicodedata import decimal
from yaml import serialize
from transactions.serializers import TransactionSerializer,TransactionFilterSerializer,walletaddressSerializer,getnamepriceSerializer
from transactions.models import Transaction
from logs.models import logs
from users.models import CustomUser
from market.models import Mycoin
from logs.models import logs
from decimal import Decimal
from functions.addressgenrator import generate_contract_address
# Create your views here.
class TransactionView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        # get validated data from user
        # transaction_type = serializer.validated_data['type']
        transaction_type = serializer.validated_data.get('type')
        if transaction_type is None:
            raise ValidationError({"error": "فیلد type الزامی است."})
        to_address = serializer.validated_data.get('to_add')
        amount = serializer.validated_data['amount']
        status_code = Transaction.Status.Uncompleted
        # get meme coin
        coin = Mycoin.objects.get(id=1)

        amount = Decimal(amount)
        coin.price = Decimal(coin.price)
        # assign sender and receiver
        receiver = ...
        try:
            sender = self.request.user
            if transaction_type == Transaction.Type.Transfer:
                receiver = CustomUser.objects.get(address = to_address)
        except CustomUser.DoesNotExist:
            raise ValidationError({"Error":"User not found!"})

        if sender.address == coin.contractAddress or transaction_type not in [Transaction.Type.Sell, Transaction.Type.Buy,Transaction.Type.Transfer]:
            raise PermissionDenied("Access denied")
        if transaction_type == Transaction.Type.Transfer and sender.address == receiver.address :
            raise ValidationError({"Error":"The sender and receiver wallet addresses must be different"})

        # create transaction
        # amount = number of coin
        if transaction_type == Transaction.Type.Buy:
            if (amount * coin.price) <= sender.balance:
                sender.balance -= amount * coin.price
                sender.memecoin_balance += Decimal(amount)
                coin.balance += amount * coin.price
                coin.available -= Decimal(amount)
                status_code = Transaction.Status.Complete
                coin.save()
                # sender log and transaction
                transaction_obj_sender = Transaction.objects.create(
                    owner = sender,
                    type=transaction_type,
                    from_add=sender.address,
                    to_add=coin.contractAddress,
                    amount=amount,
                    status=status_code,
                )
                transaction_obj_sender.save()
                logs_obj_sender = logs.objects.create(
                    owner = sender,
                    action="Buy",
                    logDetails="Buying meme coin was successful.",
                )
                logs_obj_sender.save()
                #receiver log and transaction
            else:
                status_code = Transaction.Status.Failed
                transaction_obj_sender = Transaction.objects.create(
                    owner=sender,
                    type=transaction_type,
                    from_add=sender.address,
                    to_add=coin.contractAddress,
                    amount=amount,
                    status=status_code,
                )
                transaction_obj_sender.save()
                logs_obj_sender = logs.objects.create(
                    owner=sender,
                    action="Failed purchase",
                    logDetails="Buying meme coins was unsuccessful.",
                )
                logs_obj_sender.save()
                raise ValidationError({"Error": "insufficient balance"})
        # amount = memecoin count
        elif transaction_type == Transaction.Type.Sell:
            if sender.memecoin_balance >= amount:
                 sender.memecoin_balance -= amount
                 sender.balance += (amount * coin.price)
                 coin.available += amount
                 coin.balance -= (amount * coin.price)
                 status_code  = Transaction.Status.Complete
                 coin.save()
                 # sender log and transaction
                 transaction_obj_sender = Transaction.objects.create(
                     owner=sender,
                     type=transaction_type,
                     from_add=sender.address,
                     to_add=coin.contractAddress,
                     amount=(amount*coin.price),
                     status=status_code,
                 )
                 transaction_obj_sender.save()
                 logs_obj_sender = logs.objects.create(
                     owner=sender,
                     action="Sell",
                     logDetails="selling meme coin was successful.",
                 )
                 logs_obj_sender.save()
            else:
                status_code = Transaction.Status.Failed
                transaction_obj_sender = Transaction.objects.create(
                    owner=sender,
                    type=transaction_type,
                    from_add=sender.address,
                    to_add=coin.contractAddress,
                    amount=(amount * coin.price),
                    status=status_code,
                )
                transaction_obj_sender.save()
                logs_obj_sender = logs.objects.create(
                    owner=sender,
                    action="Sell Failed",
                    logDetails="selling meme coin was unsuccessful.",
                )
                logs_obj_sender.save()
                raise ValidationError({"Error": "insufficient balance"})
        elif transaction_type == Transaction.Type.Transfer:
            if sender.memecoin_balance >= amount:
                sender.memecoin_balance -= amount
                receiver.memecoin_balance += amount
                status_code = Transaction.Status.Complete
                receiver.save()
                # sender log and transaction
                transaction_obj_sender = Transaction.objects.create(
                    owner=sender,
                    type=transaction_type,
                    from_add=sender.address,
                    to_add=receiver.address,
                    amount=amount,
                    status=status_code,
                )
                transaction_obj_sender.save()
                logs_obj_sender = logs.objects.create(
                    owner=sender,
                    action="Transfer",
                    logDetails="Transfer meme coin was successful.",
                )
                logs_obj_sender.save()
                # receiver log and transaction
                transaction_obj_receiver = Transaction.objects.create(
                    owner=receiver,
                    type=Transaction.Type.Transfer,
                    from_add=sender.address,
                    to_add=receiver.address,
                    amount=amount,
                    status=status_code,
                )
                transaction_obj_receiver.save()
                logs_obj_receiver = logs.objects.create(
                    owner=receiver,
                    action="Transfer",
                    logDetails="receive meme coin was successful.",
                )
                logs_obj_receiver.save()
            else:
                logs_obj_sender = logs.objects.create(
                    owner=sender,
                    action="Transfer Failed",
                    logDetails="Transfer meme coin was unsuccessful.",
                )
                logs_obj_sender.save()
                status_code = Transaction.Status.Failed
                transaction_obj_sender = Transaction.objects.create(
                    owner=sender,
                    type=transaction_type,
                    from_add=sender.address,
                    to_add=receiver.address,
                    amount=amount,
                    status=status_code,
                )
                transaction_obj_sender.save()
                raise ValidationError({"Error": "insufficient balance"})
        else:
            logs_obj_sender = logs.objects.create(
                owner=sender,
                action="Permission denied",
                logDetails="Permission denied",
            )
            logs_obj_sender.save()
            status_code = Transaction.Status.Failed
            transaction_obj_sender = Transaction.objects.create(
                owner=sender,
                type=transaction_type,
                from_add=sender.address,
                to_add="",
                amount=amount,
                status=status_code,
            )
            transaction_obj_sender.save()

        # save changes in DB
        sender.save()

        serializer.instance = transaction_obj_sender
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        request.user.refresh_from_db()
        transactions_instance = serializer.instance
        response_data = {
            "new_memecoin_balance": request.user.memecoin_balance,
            "transaction_type": transactions_instance.type,
            "transaction_status": transactions_instance.status,
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

#
class getAddbalance(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get user balance",
        description="Returns the balance and memecoin balance of the authenticated user.",
        responses={
            200: OpenApiResponse(
                description="Successful response",
                response={
                    "type": "object",
                    "properties": {
                        "balance": {
                            "type": "number",
                            "format": "decimal",
                        },
                        "memecoin_balance": {
                            "type": "number",
                            "format": "decimal",
                        },
                    },
                },
            ),
        },
    )
    def get(self, request):
        try:
            print(f"data is here:{self.request.data}")
            balance = request.user.balance
            memecoin_balance = request.user.memecoin_balance
            return Response({"balance": balance, "memecoin_balance": memecoin_balance}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Deposit money",
        description="Allows users to deposit money into their balance. Balance must be greater than 0.",
        request={
            "type": "object",
            "properties": {
                "balance": {"type": "number","format": "decimal", "description": "The amount to deposit."},
            },
            "required": ["balance"],
        },
        responses={
            200: OpenApiResponse(
                description="Deposit successful",
                response={
                    "type": "object",
                    "properties": {
                        "new_balance": {"type": "integer", "description": "The updated balance after deposit."},
                    },
                },
            ),
            400: OpenApiResponse(
                description="Bad request",
                response={
                    "type": "object",
                    "properties": {
                        "Error": {"type": "string", "example": "balance cannot be empty"},
                    },
                },
            ),
        },
    )

    def post(self, request):
        balance = self.request.data.get("balance")
        user = self.request.user
        if balance is None or balance <= 0:
            transaction_obj = Transaction.objects.create(
                owner=user,
                type=Transaction.Type.Deposit,
                amount=0,
                status=Transaction.Status.Failed,
            )
            transaction_obj.save()
            log = logs.objects.create(
                owner=user,
                action = "Deposit",
                logDetails="Deposit unsuccessful",
            )
            log.save()
            return Response({"Error": "balance cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
        user.balance += balance
        user.save()
        request.user.refresh_from_db()
        transaction_obj = Transaction.objects.create(
            owner=user,
            type=Transaction.Type.Deposit,
            amount=balance,
            status=Transaction.Status.Complete,
        )
        transaction_obj.save()
        log = logs.objects.create(
            owner=user,
            action="Deposit",
            logDetails="Deposit successful",
        )
        log.save()
        return Response({"new_balance": user.balance}, status=status.HTTP_200_OK)

class TransactionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(owner=user).order_by("-time")

class Transactionfilter(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=TransactionFilterSerializer,
        responses=TransactionSerializer(many=True),
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
        if min_amount and max_amount:
            queryset = queryset.filter(amount__gte=min_amount, amount__lte=max_amount)
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        sender_name = filters.get('sender_name', None)
        if sender_name:
            queryset = queryset.filter(
                Q(owner__username__icontains=sender_name)
            )
            if queryset is None:
                raise ValidationError({"Error": "sender with this username does not exist"})

        receiver_name = filters.get('receiver_name', None)
        address = ""
        if receiver_name:
            try:
                receiver_address = CustomUser.objects.get(
                    Q(username__icontains=receiver_name)
                )
                address = receiver_address.address
            except CustomUser.DoesNotExist:
                raise ValidationError({"Error": "receiver with this username does not exist"})

            queryset = queryset.filter(
                to_add=address
            )
            if not queryset.exists():
                return Response({"Error": "No transactions found."}, status=status.HTTP_404_NOT_FOUND)

        result = TransactionSerializer(queryset, many=True)
        return Response(result.data, status=status.HTTP_200_OK)

class WalletAddressView(generics.RetrieveAPIView):
    serializer_class = walletaddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        responses=walletaddressSerializer,
        description="Filter transactions based on date range, amount, sender, and receiver",
        summary="Filter Transactions"
    )
    def get_object(self):
        return self.request.user

# get name and price of meme coin
class getcoin(generics.RetrieveAPIView):
    serializer_class = getnamepriceSerializer
    # permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        methods=["GET"],
        responses=getnamepriceSerializer,
        description="Filter coin based name and price ",
        summary="Filter Mycoin"
    )
    def get_object(self):
        return Mycoin.objects.get(id=1)