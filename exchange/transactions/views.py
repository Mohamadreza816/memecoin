from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import generics , permissions,status
from transactions.serializers import TransactionSerializer
from transactions.models import Transaction
from logs.models import logs
from users.models import CustomUser
from market.models import Mycoin
from logs.models import logs
from functions.addressgenrator import generate_contract_address
# Create your views here.
class TransactionView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        # get validated data from user
        transaction_type = serializer.validated_data['type']
        to_address = serializer.validated_data['to_add']
        amount = serializer.validated_data['amount']
        status_code = Transaction.Status.Uncompleted
        # create meme coin
        obj,created = Mycoin.objects.get_or_create(
            owner = CustomUser.objects.get(id=6),
            available = 1000,
            contractAddress=generate_contract_address(),
            name = "south korean president(SKP)",
            price = 2
        )
        # save coin in DB
        coin = obj
        if created:
            coin.save()
        # assign sender and receiver
        receiver = ...
        if transaction_type == Transaction.Type.Buy or transaction_type == Transaction.Type.Sell:
            receiver = coin.owner
        else:
            receiver = CustomUser.objects.create_user(address = to_address)
        if not receiver:
            raise ValidationError({"Error":"User not found!"})
        try:
            sender = self.request.user
        except CustomUser.DoesNotExist:
            raise ValidationError({"Error":"User not found!"})

        if sender.address == receiver.address or transaction_type not in [Transaction.Type.Sell, Transaction.Type.Buy,Transaction.Type.Transfer]:
            raise PermissionDenied("Access denied")

        # create transaction
        transaction_obj_sender = ...
        transaction_obj_receiver = ...
        logs_obj_sender = ...
        logs_obj_receiver = ...
        if transaction_type == Transaction.Type.Buy:
            if amount <= sender.balance:
                sender.balance -= amount
                sender.memecoin_balance += (amount / coin.price)
                coin.owner.balance += amount
                coin.available -= (amount / coin.price)
                status_code = Transaction.Status.Complete
                # sender log and transaction
                transaction_obj_sender = Transaction.objects.create(
                    owner = sender,
                    type=transaction_type,
                    from_address=sender.address,
                    to_add=coin.owner.address,
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
                transaction_obj_receiver = Transaction.objects.create(
                    owner = coin.owner,
                    type=Transaction.Type.Sell,
                    from_add=sender.address,
                    to_add=coin.owner.address,
                    amount=amount,
                    status=status_code,
                )
                transaction_obj_receiver.save()
                logs_obj_receiver = logs.objects.create(
                    owner = coin.owner,
                    action="Sell",
                    logDetails="Selling meme coin was successful.",
                )
                logs_obj_receiver.save()
            else:
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
                 coin.owner.balance -= (amount * coin.price)
                 status_code  = Transaction.Status.Complete
                 # sender log and transaction
                 transaction_obj_sender = Transaction.objects.create(
                     owner=sender,
                     type=transaction_type,
                     from_address=sender.address,
                     to_add=coin.owner.address,
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
                 # receiver log and transaction
                 transaction_obj_receiver = Transaction.objects.create(
                     owner=coin.owner,
                     type=Transaction.Type.Buy,
                     from_add=sender.address,
                     to_add=coin.owner.address,
                     amount=amount,
                     status=status_code,
                 )
                 transaction_obj_receiver.save()
                 logs_obj_receiver = logs.objects.create(
                     owner=coin.owner,
                     action="Sell",
                     logDetails="Selling meme coin was successful.",
                 )
                 logs_obj_receiver.save()
            else:
                logs_obj_sender = logs.objects.create(
                    owner=sender,
                    action="Sell Failed",
                    logDetails="selling meme coin was unsuccessful.",
                )
                logs_obj_sender.save()
                raise ValidationError({"Error": "insufficient balance"})
        elif transaction_type == Transaction.Type.Transfer:
            if sender.memecoin_balance <= amount:
                sender.memecoin_balance -= amount
                receiver.memecoin_balance += amount
                status_code = Transaction.Status.Complete
                receiver.save()
                # sender log and transaction
                transaction_obj_sender = Transaction.objects.create(
                    owner=sender,
                    type=transaction_type,
                    from_address=sender.address,
                    to_add=receiver.address,
                    amount=amount,
                    status=status_code,
                )
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
                    to_add=coin.owner.address,
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
                from_address=sender.address,
                to_add=coin.owner.address,
                amount=amount,
                status=status_code,
            )
            transaction_obj_sender.save()

        # save changes in DB
        coin.save()
        coin.owner.save()
        sender.save()

