from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    userReference = models.ForeignKey(User)
    interest = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    preferences = models.CharField(max_length=200)
    
