# Generated by Django 5.0.7 on 2024-11-01 14:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('ip', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('cpu', models.CharField(max_length=128)),
                ('node_name', models.CharField(max_length=64)),
                ('os', models.CharField(max_length=64)),
                ('version', models.CharField(max_length=64)),
                ('recent_status', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='CommandHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('command', models.CharField(max_length=512)),
                ('response', models.CharField(max_length=1024)),
                ('ip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UI.connection')),
            ],
        ),
    ]
