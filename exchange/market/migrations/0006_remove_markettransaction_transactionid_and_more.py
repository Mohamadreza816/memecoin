# Generated by Django 4.2.19 on 2025-03-06 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_alter_mycoin_available'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='markettransaction',
            name='transactionID',
        ),
        migrations.DeleteModel(
            name='MarketQueue',
        ),
        migrations.DeleteModel(
            name='MarketTransaction',
        ),
    ]
