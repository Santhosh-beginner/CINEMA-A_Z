from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class newuser(UserCreationForm):
    """form for getting the new user's details (username, email and password)
    """
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ["username","email","password1","password2"]