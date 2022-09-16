from django.db import models
from leagues.models import League
from main.models import Player, SleeperUser
from rosters.models import Roster

# Create your models here.

class Transaction(models.Model):
    league_id = models.ForeignKey(League, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=80, primary_key=True)
    leg = models.PositiveSmallIntegerField()
    created = models.DateTimeField()
    status_updated = models.DateTimeField()
    status = models.CharField(max_length=80)
    creator = models.ForeignKey(SleeperUser, on_delete=models.RESTRICT)
    roster_ids = models.ManyToManyField(Roster)
    consenter_ids = models.JSONField(null=True)
    draft_picks = models.JSONField(null=True)
    waiver_budget = models.JSONField(null=True)
    metadata = models.JSONField(null=True)
    settings = models.JSONField(null=True)

    class Meta:
        abstract = True


class Trade(Transaction):
    players = models.ManyToManyField(Player)
    adds = models.JSONField(null=True)
    drops = models.JSONField(null=True)
    def __str__(self):
        return f'Trade: {self.transaction_id}'


class Waiver(Transaction):
    adds = models.ManyToManyField(Player, related_name='waiver_adds')
    drops = models.ManyToManyField(Player, related_name='waiver_drops')
    def __str__(self):
        return f'Waiver: {self.transaction_id}'


class FreeAgent(Transaction):
    adds = models.ManyToManyField(Player, related_name='fa_adds')
    drops = models.ManyToManyField(Player, related_name='fa_drops')
    def __str__(self):
        return f'Free Agent: {self.transaction_id}'


class Commissioner(Transaction):
    adds = models.ManyToManyField(Player, related_name='commissioner_adds')
    drops = models.ManyToManyField(Player, related_name='commissioner_drops')
    def __str__(self):
        return f'Commissioner: {self.transaction_id}'