# Generated by Django 3.1.7 on 2021-03-09 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
