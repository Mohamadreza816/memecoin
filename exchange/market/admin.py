from django.contrib import admin
from market.models import Mycoin
# Register your models here.

@admin.register(Mycoin)
class MycoinAdmin(admin.ModelAdmin):
    pass