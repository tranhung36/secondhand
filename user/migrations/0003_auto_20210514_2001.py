# Generated by Django 3.1.7 on 2021-05-14 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20210512_1650'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='data_join',
            new_name='date_join',
        ),
    ]
