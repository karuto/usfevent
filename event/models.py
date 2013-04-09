from django.db import models
from django.contrib import admin
from django.forms import ModelForm
from accounts.models import UserProfile
from taggit.managers import TaggableManager

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length = 100)
    body = models.TextField()
    refer = models.URLField()
    created = models.DateTimeField()
    tags = TaggableManager()
    flagged = models.BooleanField(default = False)
    #image1 = models.ImageField(upload_to="images/eventthumb")

    def __unicode__(self):
        return self.title
        

class Comment(models.Model):
    user = models.ForeignKey(UserProfile)
    event = models.ForeignKey(Event)
    content = models.TextField()
    time = models.DateTimeField(auto_now=True)
    
    def __unicode(self):
        return unicode("%s: %s" % (self.event, self.content[:50]))
        
class CommentAdmin(admin.ModelAdmin):
    display_fields = []
admin.site.register(Comment, CommentAdmin)

#class CommentForm(ModelForm):
#    class Meta:
#        model = Book

