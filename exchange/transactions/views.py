from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import generics , permissions,status
from transactions.serializers import TransactionSerializer
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
        print(f"DEBUG: Raw to_add from request: {to_address} (type: {type(to_address)})")
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