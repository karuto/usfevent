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
        

class Order(models.Model):
    created_time = models.DateTimeField(auto_now=True)
    client_name = models.CharField(max_length=100)
    client_org = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=100)
    client_email = models.EmailField(max_length=75)
    client_is_sponsored = models.BooleanField(default=False)
    project_name = models.CharField(max_length=100)
    project_deadline = models.DateTimeField(default=datetime.now)
    event_location = models.CharField(max_length=100)
    event_time = models.DateTimeField(default=datetime.now)
    design_text = models.TextField()
    design_concept = models.TextField()
    is_poster = models.BooleanField(default=False)
    is_flyer = models.BooleanField(default=False)
    is_handbill = models.BooleanField(default=False)
    is_businesscard = models.BooleanField(default=False)
    is_pamphlet = models.BooleanField(default=False)
    is_invitation = models.BooleanField(default=False)
    is_logo = models.BooleanField(default=False)
    is_banner = models.BooleanField(default=False)
    is_other = models.BooleanField(default=False)
    project_other = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return unicode("Project %s by %s" % (self.project_name, self.client_name))

class OrderAdmin(admin.ModelAdmin):
    display_fields = []
admin.site.register(Order, OrderAdmin)    


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

