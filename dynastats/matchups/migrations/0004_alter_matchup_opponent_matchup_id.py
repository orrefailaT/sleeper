# Generated by Django 4.1 on 2022-09-08 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matchups', '0003_alter_matchup_opponent_matchup_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchup',
            name='opponent_matchup_id',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.RESTRICT, to='matchups.matchup'),
        ),
    ]
