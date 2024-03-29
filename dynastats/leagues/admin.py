from django.contrib import admin

from .models import League


# Register your models here.
class LeagueAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(League, LeagueAdmin)