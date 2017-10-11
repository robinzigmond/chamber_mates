# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.context_processors import csrf
from .forms import UserRegistrationForm

# Create your views here.
def register(request):
    """
    a view to process the user registration form. Uses the Django default, the "clever" stuff
    is in the "edit profile" form!
    """
    if request.method=="POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user = auth.authenticate(username=request.POST.get("username"),
                                     email=request.POST.get("email"),
                                     password=request.POST.get("password1"))

            if user:
                auth.login(request, user)
                return redirect(reverse("profile"))
            else:
                messages.error(request, "Oops, something went wrong! Please review your details and try again.")
    
    else:
        form = UserRegistrationForm()
    
    args = {"active": "register", "form": form}
    args.update(csrf(request))

    return render(request, "accounts/register.html", args)


def logout(request):
    """
    a view to logout the user, and redirect them to the homepage
    """
    auth.logout(request)
    messages.success(request, "You have logged out")
    return redirect(reverse("home"))


@login_required(login_url=reverse_lazy("login"))
def profile(request):
    """
    simple view to display the user's profile page, and distinguish whether the user has just
    registered or not
    """
    return render(request, "accounts/profile.html", {"active": "profile"})


def login(request):
    """
    A view to handle the login page and form
    """
    if request.method=="POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(username=request.POST.get("username"),
                                     password=request.POST.get("password"))
            if user:
                auth.login(request, user)
                return redirect(reverse("profile"))
            else:
                messages.error(request, "Invalid username or password")

    else:
        form = AuthenticationForm()
    
    args = {"active": "login", "form": form}
    args.update(csrf(request))

    return render(request, "accounts/login.html", args)
