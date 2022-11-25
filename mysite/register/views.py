from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from .forms import newuser


# Create your views here.
def register(response):
    """Called if a request is sent to register/ url. Creates a new user from the post details and redirects to /login url
    """
    if response.method == "POST":
        form =newuser(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form=newuser()
    return render(response,"register/register.html",{"form" :form})

# Create your views here.
