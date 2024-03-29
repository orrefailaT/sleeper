from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import make_aware


# Create your models here.
class SleeperUser(models.Model):
    user_id = models.CharField(max_length=64, primary_key=True)
    display_name = models.CharField(max_length=64)
    avatar = models.CharField(max_length=64, null=True)
    site_user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    all_seasons_crawled = models.BooleanField(default=False)
    last_crawled = models.DateTimeField(default=make_aware(datetime(1970, 1, 1)))


class Player(models.Model):
    player_id = models.CharField(max_length=16, primary_key=True)
    full_name = models.CharField(max_length=64)
    search_full_name = models.CharField(max_length=64)
    search_last_name = models.CharField(max_length=64)
    status = models.CharField(max_length=32, null=True)
    team = models.CharField(max_length=16, null=True)
    fantasy_positions = models.JSONField(null=True)
    depth_chart_position = models.CharField(max_length=80, null=True)
    depth_chart_order = models.PositiveSmallIntegerField(null=True)
    practice_participation = models.CharField(max_length=64, null=True)
    practice_description = models.CharField(max_length=64, null=True)
    injury_status = models.CharField(max_length=64, null=True)
    injury_body_part = models.CharField(max_length=64, null=True)
    injury_notes = models.CharField(max_length=256, null=True)
    injury_date = models.DateField(null=True)
    years_exp = models.PositiveSmallIntegerField(null=True)
    birth_date = models.DateField(null=True)
    weight = models.CharField(max_length=4, null=True)
    height = models.CharField(max_length=16, null=True)
    college = models.CharField(max_length=32, null=True)

    def __str__(self):
        return f'{self.player_id}: {self.full_name}'
