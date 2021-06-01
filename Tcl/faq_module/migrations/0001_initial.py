# Generated by Django 3.0.8 on 2020-12-16 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FAQModel',
            fields=[
                ('faq_id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(default=1)),
                ('deleted', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'FAQ_table',
            },
        ),
    ]