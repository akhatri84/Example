# Generated by Django 2.2.17 on 2021-01-06 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0003_auto_20210106_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appusermodel',
            name='country',
            field=models.TextField(blank=True, null=True),
        ),
    ]
