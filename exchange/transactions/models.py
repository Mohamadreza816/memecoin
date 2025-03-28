from django.utils import timezone

from django.db import models
from users.models import CustomUser
# Create your models here.
class Transaction(models.Model):
    class Type(models.TextChoices):
        Buy = 'B','Buy',
        Sell = 'S','Sell',
        Withdraw = 'W','Withdraw',
        Deposit = 'D','Deposit',
        Transfer = 'T','Transfer',
        UNSET = 'U','Unset',

    class Status(models.TextChoices):
        Complete = 'C','Complete'
        Uncompleted = 'UC','Uncompleted'
        Failed = 'F','Failed'
        UNSET = 'U','Unset'

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=Type.choices,default=Type.UNSET)
    from_add = models.CharField(max_length=50)
    to_add = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=2, choices=Status.choices,default=Status.UNSET)

