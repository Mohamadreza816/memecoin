from django.contrib import admin
from logs.models import logs
# Register your models here.
@admin.register(logs)
class logsAdmin(admin.ModelAdmin):
    pass