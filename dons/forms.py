from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from dons.models import Don

class RegForm(ModelForm):
	username = forms.CharField(label=(u'Real Name'))
	email = forms.EmailField(label=(u'Email Address'))
	password = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
	password1 = forms.CharField(label=(u'Verify Password'), widget=forms.PasswordInput(render_value=False))
	
	class Meta:
		model = Don


