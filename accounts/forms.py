#coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class RegisterForm(forms.Form):
    email=forms.EmailField(label=_(u"email"),max_length=30,widget=forms.TextInput(attrs={'size': 30,}))    
    password=forms.CharField(label=_(u"password"),max_length=30,widget=forms.PasswordInput(attrs={'size': 20,}))
    username=forms.CharField(label=_(u"nickname"),max_length=30,widget=forms.TextInput(attrs={'size': 20,}))
    
    def clean_username(self):
        '''check if nickname exists'''
        users = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if not users:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_(u"this nickname has already been taken"))
        
    def clean_email(self):
        '''check if email exists'''
        emails = User.objects.filter(email__iexact=self.cleaned_data["email"])
        if not emails:
            return self.cleaned_data["email"]
        raise forms.ValidationError(_(u"this email has already been taken"))
        
class LoginForm(forms.Form):
    username=forms.CharField(label=_(u"nickname"),max_length=30,widget=forms.TextInput(attrs={'size': 20,}))
    password=forms.CharField(label=_(u"password"),max_length=30,widget=forms.PasswordInput(attrs={'size': 20,}))
    
