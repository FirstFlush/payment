# Generated by Django 4.0.3 on 2022-10-31 19:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hmac_auth', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hmackey',
            old_name='user',
            new_name='account_id',
        ),
    ]
