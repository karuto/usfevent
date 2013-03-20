from django.db import models
from taggit.managers import TaggableManager

# Create your models here.
class Event(models.Model):
	title = models.CharField(max_length=100)
	body = models.TextField()
	created = models.DateTimeField()
	tags = TaggableManager()
	
	def __unicode__(self):
		return self.title
