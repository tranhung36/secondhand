# Generated by Django 3.1.7 on 2021-05-19 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_profile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
