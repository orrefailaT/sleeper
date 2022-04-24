from django.contrib import admin

from .models import Roster

# Register your models here.

class RosterAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Roster, RosterAdmin)