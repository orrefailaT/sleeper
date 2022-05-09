from django.contrib import admin

from .models import Roster, Draft, Pick

# Register your models here.

class RosterAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

class DraftAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

class PickAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Roster, RosterAdmin)
admin.site.register(Draft, DraftAdmin)
admin.site.register(Pick, PickAdmin)