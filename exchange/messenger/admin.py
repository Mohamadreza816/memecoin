from django.contrib import admin
from messenger.models import *
# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass