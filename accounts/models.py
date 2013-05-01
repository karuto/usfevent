from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    django_user = models.ForeignKey(User)
    firstname = models.CharField(max_length=200, default="Default Firstname")
    lastname = models.CharField(max_length=200, default="Default Lastname")
    position = models.CharField(max_length=200)
    interest = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    preferences = models.CharField(max_length=200)
    bio = models.CharField(max_length=200)
    avatar = models.ImageField('picture',upload_to='uploadImages', default='static/avatar_blank.jpg')
    #is_moderator = models.BooleanField(default = False)
    #is_superuser = models.BooleanField(default = False)

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
    
