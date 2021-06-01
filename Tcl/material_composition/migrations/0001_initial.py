# Generated by Django 3.0.8 on 2020-12-15 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialCompositionModel',
            fields=[
                ('materialcomposition_id', models.AutoField(primary_key=True, serialize=False)),
                ('material_name', models.TextField()),
                ('percentage', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(default=1)),
                ('deleted', models.IntegerField(default=0)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.ProductModel')),
            ],
            options={
                'db_table': 'material_composition',
            },
        ),
    ]