from django.contrib import admin

from .models import Matchup

# Register your models here.
class MatchupAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Matchup, MatchupAdmin)