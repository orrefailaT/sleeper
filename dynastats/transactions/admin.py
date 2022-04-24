from django.contrib import admin

from .models import Commissioner, FreeAgent, Trade, Transaction, Waiver

# Register your models here.
admin.site.register(FreeAgent)
admin.site.register(Waiver)
admin.site.register(Trade)
admin.site.register(Commissioner)