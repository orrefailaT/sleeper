# Generated by Django 4.1 on 2022-09-10 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0006_alter_league_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='last_import_successful',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
