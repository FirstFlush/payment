# Generated by Django 4.0.3 on 2022-10-06 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0005_cryptoaddress_is_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptowallet',
            name='vendor_key',
            field=models.CharField(default='fdsjakfjksadlfsaf', max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
