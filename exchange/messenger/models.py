from django.db import models

from users.models import CustomUser

# Create your models here.
class Message(models.Model):
    class message_status(models.TextChoices):
        Seen = 'S', 'Seen'
        Unseen = 'US', 'Unseen'
        UNSET = 'U', 'Unset'

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=100,default='')
    to_add = models.CharField(max_length=50)
    text = models.TextField(blank=False, null=False)
    file = models.FileField(upload_to='messages/files', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    m_status = models.CharField(max_length=2, choices=message_status.choices,default=message_status.UNSET)

    def __str__(self):
        return f"{self.owner} -> {self.to_add}: {self.text[:20]}"