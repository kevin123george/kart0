# Generated by Django 2.2.5 on 2019-09-30 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_delete_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='label',
        ),
    ]
