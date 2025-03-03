from django.db import models

from users.models import CustomUser

# Create your models here.
class Message(models.Model):
    class message_status(models.TextChoices):
        Seen = 'S', 'Seen'
        Unseen = 'US', 'Unseen'
        UNSET = 'U', 'Unset'

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    from_add = models.CharField(max_length=50)
    to_add = models.CharField(max_length=50)
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='messages/files', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    m_status = models.CharField(max_length=2, choices=message_status.choices,default=message_status.UNSET)
