# Generated by Django 4.0.3 on 2022-10-16 03:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0023_payment_price_id_paymentrequest_price_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='problem',
            new_name='is_problem',
        ),
    ]
