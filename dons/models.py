from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, AbstractBaseUser

# A very decent tutorial on the new custom user model of Django 1.5
# This thing is basically built based on that.
# http://procrastinatingdev.com/django/using-configurable-user-models-in-django-1-5/

# Create your models here.
class Don(AbstractBaseUser):
	email = models.EmailField(max_length=254, unique=True)
	name = models.CharField(max_length=100, unique=True, db_index=True)

	def __unicode__(self):
		return self.name

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['name']

"""
# No longer supported in Django 1.5, comment it out
# Create our user object to attach to our Don object
def create_don_user_callback(sender, instance, **kwargs):
	don, new = Don.objects.get_or_create(user = instance)
post_save.connect(create_don_user_callback, User)
"""



