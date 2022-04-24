from django.db import models

# Create your models here.
class Player(models.Model):
    player_id = models.CharField(max_length=16, primary_key=True)
    full_name = models.CharField(max_length=64)
    status = models.CharField(max_length=32, null=True)
    team = models.CharField(max_length=16, null=True)
    fantasy_positions = models.JSONField(null=True)
    depth_chart_position = models.CharField(max_length=80, null=True)
    depth_chart_order = models.IntegerField(null=True)
    practice_participation = models.CharField(max_length=64, null=True)
    practice_description = models.CharField(max_length=64, null=True)
    injury_status = models.CharField(max_length=64, null=True)
    injury_body_part = models.CharField(max_length=64, null=True)
    injury_notes = models.CharField(max_length=256, null=True)
    injury_date = models.DateField(null=True)
    years_exp = models.IntegerField(null=True)
    birth_date = models.DateField(null=True)
    weight = models.CharField(max_length=4, null=True)
    height = models.CharField(max_length=16, null=True)
    college = models.CharField(max_length=32, null=True)

    def __str__(self):
        return f'{self.player_id}: {self.full_name}'
"""
class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=80)
    username = models.CharField(max_length=80)
    display_name = models.CharField(max_length=80)
    avatar = models.CharField(max_length=80)
    metadata = models.JSONField()

    def __str__(self):
        return self.display_name


class Roster(models.Model):
    taxi = models.JSONField()
    starters = models.JSONField()
    settings = models.JSONField()
    roster_id = models.IntegerField()
    reserve = models.JSONField()
    players = models.JSONField()
    owner_id = models.CharField(max_length=80)
    league_id = models.CharField(max_length=80)

    def __str__(self):
        return self.roster_id

"""
