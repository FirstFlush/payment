# Generated by Django 4.0.3 on 2022-10-11 04:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0015_alter_payment_btc_confirmed_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('btc_unconfirmed', models.DecimalField(decimal_places=7, default=0, max_digits=10)),
                ('btc_confirmed', models.DecimalField(decimal_places=7, default=0, max_digits=10)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('address_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.cryptoaddress')),
            ],
        ),
    ]
