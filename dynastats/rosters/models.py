from django.db import models

from leagues.models import League
from main.models import Player, SleeperUser

# Create your models here.
class Roster(models.Model):
    league_id = models.ForeignKey(League, on_delete=models.CASCADE)
    roster_id = models.CharField(max_length=64, primary_key=True)
    owner_id = models.ForeignKey(SleeperUser, on_delete=models.RESTRICT, null=True)
    team_name = models.CharField(max_length=256)
    players = models.ManyToManyField(Player, related_name='+')
    starters = models.ManyToManyField(Player, related_name='+')
    taxi = models.ManyToManyField(Player, related_name='+')
    reserve = models.ManyToManyField(Player, related_name='+')
    settings = models.JSONField()
    co_owners = models.ManyToManyField(SleeperUser, related_name='co_owners')


class Draft(models.Model):
    league_id = models.ForeignKey(League, on_delete=models.CASCADE)
    draft_id = models.CharField(max_length=64, primary_key=True)
    type = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    start_time = models.DateTimeField(null=True)
    slot_to_roster_id = models.JSONField()
    settings = models.JSONField()
    season_type = models.CharField(max_length=32)
    season = models.CharField(max_length=4)
    draft_order = models.JSONField()
    metadata = models.JSONField(null=True)


class Pick(models.Model):
    pick_id = models.CharField(max_length=64, primary_key=True)
    round = models.PositiveSmallIntegerField()
    roster_id = models.ForeignKey(Roster, on_delete=models.RESTRICT)
    player_id = models.ForeignKey(Player, on_delete=models.RESTRICT)
    picked_by = models.ForeignKey(SleeperUser, on_delete=models.RESTRICT, null=True)
    pick_no = models.PositiveSmallIntegerField()
    metadata = models.JSONField(null=True)
    draft_slot = models.PositiveSmallIntegerField()
    draft_id = models.ForeignKey(Draft, on_delete=models.CASCADE)