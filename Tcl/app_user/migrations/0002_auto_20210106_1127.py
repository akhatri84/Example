# Generated by Django 2.2.17 on 2021-01-06 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appusermodel',
            name='city',
            field=models.TextField(null=True),
        ),
    ]
