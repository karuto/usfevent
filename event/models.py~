from django.db import models
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
