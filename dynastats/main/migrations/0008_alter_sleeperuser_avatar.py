# Generated by Django 4.1 on 2022-09-08 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_rename_search_first_name_player_search_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sleeperuser',
            name='avatar',
            field=models.CharField(max_length=64, null=True),
        ),
    ]