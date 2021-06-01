# Generated by Django 3.0.8 on 2021-03-31 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_productmodel_colors'),
        ('impactsize', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='impactsizemodel',
            name='impact_per_size',
        ),
        migrations.AddField(
            model_name='impactsizemodel',
            name='attribute_value',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.AttributeValueModel'),
        ),
    ]
