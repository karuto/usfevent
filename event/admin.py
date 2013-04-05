from django.contrib import admin
from event.models import Event

# admin.site.register(Event)

class EventAdmin(admin.ModelAdmin):
	fields = []
#	fields = ['refer', 'referral']
admin.site.register(Event, EventAdmin)
