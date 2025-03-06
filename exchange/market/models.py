from django.db import models
from users.models import CustomUser
from transactions.models import Transaction
from functions.addressgenrator import generate_contract_address
# Create your models here.
class Mycoin(models.Model):
    available = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    contractAddress = models.CharField(max_length=50,unique=True)
    name = models.CharField(max_length=50,default='Oscar')
    price = models.DecimalField(max_digits=10,decimal_places=2)
    balance = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    def save(self, *args, **kwargs):
        if not self.contractAddress:
            self.contractAddress = generate_contract_address()
        super().save(*args, **kwargs)

