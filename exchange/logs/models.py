from django.db import models
from users.models import CustomUser
# Create your models here.
class logs(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=30)
    logDetails = models.TextField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)