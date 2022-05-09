from django.db import models

from leagues.models import League
from main.models import Player
from rosters.models import Roster

# Create your models here.
class Matchup(models.Model):
    league_id = models.ForeignKey(League, on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField()
    matchup_id = models.CharField(max_length=128, primary_key=True)
    opponent_matchup_id = models.OneToOneField('self', on_delete=models.RESTRICT, null=True, db_constraint=False)
    roster_id = models.ForeignKey(Roster, on_delete=models.RESTRICT)
    starters = models.ManyToManyField(Player, related_name='+')
    starters_points = models.JSONField()
    players = models.ManyToManyField(Player, related_name='+')
    players_points = models.JSONField()
    points = models.FloatField()
    custom_points = models.FloatField(null=True)
    