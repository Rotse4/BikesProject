# Generated by Django 5.1 on 2024-08-28 12:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_test_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='permission',
            table='Permission',
        ),
        migrations.AlterModelTable(
            name='role',
            table='Role',
        ),
        migrations.AlterModelTable(
            name='shopuser',
            table='ShopUser',
        ),
    ]