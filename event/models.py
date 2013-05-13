from accounts.models import UserProfile
from datetime import datetime  
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from taggit.managers import TaggableManager

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    refer = models.URLField(blank=True)
    created = models.DateTimeField(auto_now=True)
    event_time = models.DateTimeField(default=datetime.now)
    location = models.CharField(max_length=100, default="USF Graphics Center")
    tags = TaggableManager()
    flagged = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    image1 = models.ImageField('picture',upload_to='uploadImages', default='static/event_blank.jpg')
    author = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return self.title
        

#class Order(models.Model):



class Comment(models.Model):
    user = models.ForeignKey(UserProfile)
    event = models.ForeignKey(Event)
    content = models.TextField()
    time = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return unicode("%s: %s" % (self.event, self.content[:50]))
        
        
class CommentAdmin(admin.ModelAdmin):
    display_fields = []
admin.site.register(Comment, CommentAdmin)    


class Like(models.Model):
    user = models.ForeignKey(UserProfile)
    event = models.ForeignKey(Event)
    time = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return str(self.user.django_user) + " likes " +(self.event.title)
    
class LikeAdmin(admin.ModelAdmin):
    display_fields = []
admin.site.register(Like, LikeAdmin)

