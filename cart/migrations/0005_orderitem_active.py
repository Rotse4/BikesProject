# Generated by Django 5.1 on 2025-01-15 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_alter_orderitem_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='active',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
