# Generated by Django 2.2.5 on 2019-10-04 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_remove_address_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sport wear'), ('OW', 'Outwear'), ('CL', 'Classy'), ('EW', 'Ethnic Wear'), ('WW', 'Western Wear'), ('FW', 'Fusion Wear'), ('LJ', 'Leggings & Jeggings')], max_length=2),
        ),
    ]
