# Generated by Django 3.0.8 on 2021-02-25 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_remove_productmodel_product_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributevaluemodel',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]
