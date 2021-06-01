# Generated by Django 3.0.8 on 2021-01-19 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_productmodel_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeModel',
            fields=[
                ('attribute_id', models.AutoField(primary_key=True, serialize=False)),
                ('attribute_name', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(default=1)),
                ('deleted', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'attribute',
            },
        ),
        migrations.CreateModel(
            name='AttributeValueModel',
            fields=[
                ('attribute_value_id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(default=1)),
                ('deleted', models.IntegerField(default=0)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.AttributeModel')),
            ],
            options={
                'db_table': 'attribute_value',
            },
        ),
        migrations.RemoveField(
            model_name='productmodel',
            name='colors',
        ),
        migrations.RemoveField(
            model_name='productmodel',
            name='size',
        ),
        migrations.CreateModel(
            name='ProductAttributeModel',
            fields=[
                ('product_attribute_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(default=1)),
                ('deleted', models.IntegerField(default=0)),
                ('attribute_value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.AttributeValueModel')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.ProductModel')),
            ],
            options={
                'db_table': 'product_attribute',
            },
        ),
    ]
