# Generated by Django 5.0.3 on 2024-05-07 16:56

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='deleted_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='deleted_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
