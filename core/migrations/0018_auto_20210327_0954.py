# Generated by Django 3.1.7 on 2021-03-27 02:54

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0012_city_country_region_subregion'),
        ('core', '0017_auto_20210325_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='subregion',
            field=smart_selects.db_fields.ChainedForeignKey(chained_field='region', chained_model_field='region', on_delete=django.db.models.deletion.CASCADE, to='cities_light.subregion'),
        ),
    ]
