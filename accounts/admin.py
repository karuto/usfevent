from django.contrib import admin
from accounts.models import UserProfile

# admin.site.register(Event)

class UserAdmin(admin.ModelAdmin):
	fields = []
admin.site.register(UserProfile, UserAdmin)
