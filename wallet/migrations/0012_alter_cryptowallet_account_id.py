# Generated by Django 4.0.3 on 2022-10-10 00:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_vendorpayment'),
        ('wallet', '0011_cryptowallet_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptowallet',
            name='account_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.account'),
        ),
    ]
