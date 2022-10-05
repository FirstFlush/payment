# Generated by Django 4.0.3 on 2022-10-05 03:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoCoin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coin_name', models.CharField(max_length=50, unique=True)),
                ('coin_name_short', models.CharField(max_length=10, unique=True)),
            ],
            options={
                'verbose_name': 'Crypto Coin',
                'verbose_name_plural': 'Crypto Coins',
            },
        ),
        migrations.CreateModel(
            name='CryptoPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('coin_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='price.cryptocoin')),
            ],
        ),
    ]
