# Generated by Django 4.0.3 on 2022-04-24 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rosters', '0002_alter_roster_roster_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roster',
            name='id',
        ),
        migrations.AlterField(
            model_name='roster',
            name='roster_id',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
    ]
