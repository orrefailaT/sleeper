# Generated by Django 4.0.3 on 2022-04-24 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rosters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roster',
            name='roster_id',
            field=models.IntegerField(db_index=True),
        ),
    ]
