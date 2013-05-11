from accounts.models import UserProfile
from datetime import datetime  
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models


class Message(models.Model):
    msg_from = models.ForeignKey(UserProfile, related_name="msg_from")
    msg_to = models.ForeignKey(UserProfile, related_name="msg_to")
    content = models.TextField()
    time = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    def __unicode__(self):
        return str(self.msg_from) + " <== From | To ==> " +str(self.msg_to)

class MessageAdmin(admin.ModelAdmin):
    display_fields = []
admin.site.register(Message, MessageAdmin)

