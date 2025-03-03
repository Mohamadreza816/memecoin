from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import generics , permissions,status
from rest_framework.views import APIView
from django.db.models import Q
from transactions.serializers import TransactionSerializer,TransactionFilterSerializer
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
            "transaction_type": transactions_instance.get_type_display(),
            "transaction_status": transactions_instance.get_status(),
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

#Test Below classes....
class getAddbalance(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        try:
            print(f"data is here:{self.request.data}")
            balance = request.user.balance
            memecoin_balance = request.user.memecoin_balance
            return Response({"balance": balance, "memecoin_balance": memecoin_balance}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({"new_balance": user.balance}, status=status.HTTP_200_OK)

class TransactionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(owner=user).order_by("-time")

class Transactionfilter(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionFilterSerializer
    # filter_serializer_class = TransactionFilterSerializer
    queryset = Transaction.objects.filter(owner=CustomUser.objects.get(id=7))
    def post(self, request):
        return self.list(request)
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)
    def get_queryset(self):
        filter_serializer = TransactionFilterSerializer(data=self.request.data)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

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
            queryset = queryset.filter(time__gte=min_amount, time__lte=max_amount)
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        sender_name = filters.get('sender_name', None)
        if sender_name:
            queryset = queryset.filter(
                Q(owner__username__icontains=sender_name) |
                Q(owner__first_name__icontains=sender_name) |
                Q(owner__last_name__icontains=sender_name)
            )

        receiver_name = filters.get('receiver_name', None)
        if receiver_name:
            queryset = queryset.filter(
                Q(to_add__user__first_name__icontains=receiver_name) |
                Q(to_add__user__last_name__icontains=receiver_name)
            )
        return queryset