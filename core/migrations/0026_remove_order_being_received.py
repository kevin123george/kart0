# Generated by Django 2.2.5 on 2019-10-13 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20191004_1036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='being_received',
        ),
    ]
