from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    django_user = models.ForeignKey(User)
    firstname = models.CharField(max_length=200, default="Default Firstname")
    lastname = models.CharField(max_length=200, default="Default Lastname")
    bio = models.CharField(max_length=500, blank=True)
    avatar = models.ImageField('picture',upload_to='uploadImages', default='static/avatar_blank.jpg')
    graduation_year = models.IntegerField(default=2013)
    affiliation_type = models.IntegerField(default=0) # 0 stu, 1 staff, 2 faculty
    affiliation_msg = models.CharField(max_length=200, blank=True)  
    is_connected = models.BooleanField(default=False)
    #is_moderator = models.BooleanField(default=False)
    #is_superuser = models.BooleanField(default=False)

    def __unicode__(self):
        return "Linked to: " + str(self.django_user)

class Friendship(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    friend_from = models.ForeignKey(UserProfile, related_name="friend_from")
    friend_to = models.ForeignKey(UserProfile, related_name="friend_to")

    def __unicode__(self):
        return str(self.friend_from) + " <--from | to--> " + str(self.friend_to)

class FriendshipAdmin(admin.ModelAdmin):
    display_fields = []
admin.site.register(Friendship, FriendshipAdmin)
    
