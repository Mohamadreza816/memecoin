from django.db import models
from django.contrib.auth.models import AbstractUser
from functions.addressgenrator import generate_contract_address
# Create your models here.
class CustomUser(AbstractUser):
    class Type(models.TextChoices):
        regular_user = 'RU','Regular-user'
        owner = 'OW','Owner'

    address = models.CharField(max_length=50,unique=True)
    balance = models.FloatField(default=0)
    # picture = models.ImageField(upload_to='users/pictures', blank=True)
    type = models.CharField(choices=Type.choices, default=Type.regular_user, max_length=2)

    def save(self, *args, **kwargs):
        if not self.address:
            self.address = generate_contract_address()
        super().save(*args, **kwargs)
