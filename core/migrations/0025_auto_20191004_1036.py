# Generated by Django 2.2.5 on 2019-10-04 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20191004_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sport wear'), ('OW', 'Outwear'), ('CL', 'Classy'), ('EW', 'Ethnic Wear'), ('WW', 'Western Wear'), ('FW', 'Fusion Wear')], max_length=2),
        ),
    ]
