from django.db import models

# Create your models here.
class League(models.Model):
    league_id = models.CharField(primary_key=True, max_length=80)
    previous_league_id = models.OneToOneField('self', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=80)
    season = models.CharField(max_length=80)
    sport = models.CharField(max_length=80)
    status = models.CharField(max_length=80)
    total_rosters = models.IntegerField()
    season_type = models.CharField(max_length=80)
    settings = models.JSONField()
    scoring_settings = models.JSONField()
    roster_positions = models.JSONField()
    metadata = models.JSONField()
    draft_id = models.CharField(max_length=80)
    bracket_id = models.IntegerField(null=True)
    loser_bracket_id = models.IntegerField(null=True)
    avatar = models.CharField(max_length=80, null=True)

    def __str__(self):
        return self.league_id
    