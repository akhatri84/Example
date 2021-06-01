# Generated by Django 3.0.8 on 2021-01-25 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('impact_indicator', '0003_auto_20210125_1703'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImpactIndicatorFilesModel',
            fields=[
                ('impactindicatorfiles_id', models.AutoField(primary_key=True, serialize=False)),
                ('file_type', models.TextField()),
                ('file_extension', models.TextField()),
                ('aws_file_url', models.TextField()),
                ('file_size', models.TextField()),
                ('impactindicatorfile_name', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(default=1)),
                ('deleted', models.IntegerField(default=0)),
                ('impact_indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='impact_indicator.ImpactIndicatorModel')),
            ],
            options={
                'db_table': 'impact_indicator_files',
            },
        ),
    ]