# Generated by Django 4.0.3 on 2022-10-19 02:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0025_cryptowallet_vendor_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='price_id',
        ),
        migrations.RemoveField(
            model_name='paymentrequest',
            name='price_id',
        ),
    ]
