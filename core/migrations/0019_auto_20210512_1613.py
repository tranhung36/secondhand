# Generated by Django 3.1.7 on 2021-05-12 09:13

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_images_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='images',
            name='image',
            field=sorl.thumbnail.fields.ImageField(upload_to='product_images'),
        ),
    ]
