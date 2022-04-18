# Generated by Django 4.0.3 on 2022-04-17 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('league_id', models.CharField(max_length=80, primary_key=True, serialize=False)),
                ('previous_league_id', models.CharField(max_length=80)),
                ('name', models.CharField(max_length=80)),
                ('season', models.CharField(max_length=80)),
                ('sport', models.CharField(max_length=80)),
                ('status', models.CharField(max_length=80)),
                ('total_rosters', models.IntegerField()),
                ('season_type', models.CharField(max_length=80)),
                ('settings', models.JSONField()),
                ('scoring_settings', models.JSONField()),
                ('roster_positions', models.JSONField()),
                ('metadata', models.JSONField()),
                ('draft_id', models.CharField(max_length=80)),
                ('bracket_id', models.IntegerField()),
                ('loser_bracket_id', models.IntegerField()),
                ('avatar', models.CharField(max_length=80)),
            ],
        ),
    ]
