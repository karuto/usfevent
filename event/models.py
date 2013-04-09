from django.db import models
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
    image1 = models.ImageField('picture',upload_to='uploadImages')

    def __unicode__(self):
        return self.title
        

class Comment(models.Model):
    user_id = models.ForeignKey(UserProfile)
    event_id = models.ForeignKey(Event)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
