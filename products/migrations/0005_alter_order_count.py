# Generated by Django 4.2.23 on 2025-07-18 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_order_added_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
