from django import forms
from .models import Blog
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content']

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
