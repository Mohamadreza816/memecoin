from django.db import models
from users.models import CustomUser
from transactions.models import Transaction
from functions.addressgenrator import generate_contract_address
# Create your models here.
class Mycoin(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    contractAddress = models.CharField(max_length=50,unique=True)
    name = models.CharField(max_length=50,default='Oscar')
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.contractAddress:
            self.contractAddress = generate_contract_address()
        super().save(*args, **kwargs)


class MarketQueue(models.Model):
    class Type(models.TextChoices):
        Buy = 'B','Buy'
        Sell = 'S','Sell'
        UNSET = 'U','Unset'

    class Status(models.TextChoices):
        Open = 'O','Open'
        Closed = 'CL','Closed'
        Canceled = 'CA','Canceled'

    transactionID= models.ForeignKey(Transaction, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contract_add = models.ForeignKey(Mycoin, on_delete=models.CASCADE)
    type = models.CharField(max_length=1,choices=Type.choices,default=Type.UNSET)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=2,choices=Status.choices,default=Status.Canceled,blank=True)
    closeTime = models.DateTimeField()

class MarketTransaction(models.Model):
    transactionID= models.ForeignKey(Transaction, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)

