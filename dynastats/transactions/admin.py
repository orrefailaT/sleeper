from django.contrib import admin

from .models import Commissioner, FreeAgent, Trade, Waiver

# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(FreeAgent, TransactionAdmin)
admin.site.register(Waiver, TransactionAdmin)
admin.site.register(Trade, TransactionAdmin)
admin.site.register(Commissioner, TransactionAdmin)