# Generated by Django 4.0.3 on 2022-10-05 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_delete_priceapifailure'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptowallet',
            name='slug',
            field=models.SlugField(default='wat', max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
