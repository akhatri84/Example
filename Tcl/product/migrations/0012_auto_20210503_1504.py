# Generated by Django 3.0.8 on 2021-05-03 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_productmodel_detail_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productmodel',
            name='price',
            field=models.CharField(default='0,0', max_length=10),
        ),
    ]
