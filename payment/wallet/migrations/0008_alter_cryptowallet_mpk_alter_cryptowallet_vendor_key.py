# Generated by Django 4.0.3 on 2022-10-06 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0007_cryptowallet_is_vendor_alter_cryptowallet_mpk_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptowallet',
            name='mpk',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='cryptowallet',
            name='vendor_key',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
