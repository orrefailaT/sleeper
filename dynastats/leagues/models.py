from django.db import models

from main.models import SleeperUser

# Create your models here.
class League(models.Model):
    last_updated = models.DateTimeField(auto_now=True, null=True)
    league_id = models.CharField(primary_key=True, max_length=80)
    previous_league_id = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, related_name='following_league')
    name = models.CharField(max_length=80)
    season = models.CharField(max_length=80)
    sport = models.CharField(max_length=80)
    status = models.CharField(max_length=80)
    total_rosters = models.PositiveSmallIntegerField()
    season_type = models.CharField(max_length=80)
    settings = models.JSONField()
    scoring_settings = models.JSONField()
    roster_positions = models.JSONField()
    metadata = models.JSONField(null=True)
    draft_id = models.CharField(max_length=80)
    bracket_id = models.PositiveBigIntegerField(null=True)
    loser_bracket_id = models.PositiveBigIntegerField(null=True)
    avatar = models.CharField(max_length=80, null=True)
    sleeper_users = models.ManyToManyField(SleeperUser)
    last_import_successful = models.BooleanField()

    def __str__(self):
        return self.league_id
    