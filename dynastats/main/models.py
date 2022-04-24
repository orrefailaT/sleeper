from django.db import models

# Create your models here.
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
