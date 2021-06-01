# Generated by Django 3.0.8 on 2020-12-15 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiConfigModel',
            fields=[
                ('apiconfig_id', models.AutoField(primary_key=True, serialize=False)),
                ('api_key', models.TextField()),
                ('secret_key', models.TextField()),
                ('pwd', models.TextField()),
                ('apiend_point', models.TextField()),
                ('platform', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(default=1)),
                ('deleted', models.IntegerField(default=0)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_user.AppUserModel')),
            ],
            options={
                'db_table': 'api_config',
            },
        ),
    ]