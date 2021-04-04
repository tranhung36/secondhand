# Generated by Django 3.1.7 on 2021-04-03 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20210403_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingaddress',
            name='region',
        ),
        migrations.RemoveField(
            model_name='billingaddress',
            name='subregion',
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='city',
            field=models.CharField(default='Da Nang', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='district',
            field=models.CharField(default='Thanh Khe', max_length=100),
            preserve_default=False,
        ),
    ]