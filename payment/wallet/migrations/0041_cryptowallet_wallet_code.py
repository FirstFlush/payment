# Generated by Django 4.0.3 on 2022-11-06 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0040_rename_vendor_url_cryptowallet_notify_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptowallet',
            name='wallet_code',
            field=models.CharField(default='e9867e003d344bc91e4c', max_length=20),
            preserve_default=False,
        ),
    ]
