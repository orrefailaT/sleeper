from django.contrib import admin

from .models import Player, SleeperUser
# Register your models here.

class PlayerAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

class SleeperUserAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Player, PlayerAdmin)
admin.site.register(SleeperUser, SleeperUserAdmin)