# Generated by Django 3.0.8 on 2021-05-11 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_auto_20210503_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='kgco2',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='productmodel',
            name='kmtravel',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='productmodel',
            name='liter',
            field=models.IntegerField(null=True),
        ),
    ]
