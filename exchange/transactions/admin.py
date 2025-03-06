from django.contrib import admin

from transactions.models import Transaction


# Register your models here.
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass