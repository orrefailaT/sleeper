from enum import unique
from pickletools import read_long1
from django.db import models

from leagues.models import League
from main.models import Player, SleeperUser

# Create your models here.
class Roster(models.Model):
    league_id = models.ForeignKey(League, on_delete=models.CASCADE, db_index=True)
    roster_id = models.CharField(max_length=64, primary_key=True)
    owner_id = models.ForeignKey(SleeperUser, on_delete=models.RESTRICT)
    team_name = models.CharField(max_length=256)
    players = models.ManyToManyField(Player, related_name='+')
    starters = models.ManyToManyField(Player, related_name='+')
    taxi = models.ManyToManyField(Player, related_name='+')
    reserve = models.ManyToManyField(Player, related_name='+')
    settings = models.JSONField()
    co_owners = models.ManyToManyField(SleeperUser, related_name='co_owners')