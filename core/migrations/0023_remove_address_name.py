# Generated by Django 2.2.5 on 2019-10-03 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20191003_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='name',
        ),
    ]
