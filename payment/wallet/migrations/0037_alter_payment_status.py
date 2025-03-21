# Generated by Django 4.0.3 on 2022-10-26 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0036_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('paid', 'Paid'), ('underpaid', 'Underpaid'), ('overpaid', 'Overpaid'), ('orphan', 'Orphan')], max_length=255),
        ),
    ]
