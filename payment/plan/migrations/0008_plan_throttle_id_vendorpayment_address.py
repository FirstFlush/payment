# Generated by Django 4.0.3 on 2022-11-06 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0007_rename_throttleplan_throttlerate'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='throttle_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, to='plan.throttlerate'),
        ),
        migrations.AddField(
            model_name='vendorpayment',
            name='address',
            field=models.CharField(default='bleh', max_length=255),
            preserve_default=False,
        ),
    ]
