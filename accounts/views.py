# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.context_processors import csrf
from django.db import IntegrityError
from .forms import UserRegistrationForm, ProfileForm
from .models import Profile, UserInstrument

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
    view to display the user's profile page, and distinguish whether the user has completed
    their profile to the minimum standard required to be useful. If not, they are prompted to fill
    it out
    """
    user_id = User.objects.get(username=request.user.username).pk
    try:
        user_profile = Profile.objects.get(user=user_id)
        num_instruments = UserInstrument.objects.filter(user=user_id).count()
        complete = user_profile.location and user_profile.max_distance and num_instruments > 0
    except Profile.DoesNotExist:
        complete = False
    
    if request.method=="POST":
        form = ProfileForm(request.POST)
        
        if form.is_valid():
            details = form.save(False)
            details.user = request.user
            try:
                details.save()
            except IntegrityError:
                # this happens if the user already exists (because only one profile is allowed per user)
                # In other words, the user wants to update their profile. We allow this by specifying
                # the primary key when saving the model
                user_id = User.objects.get(username=request.user.username).pk
                details.pk = Profile.objects.get(user=user_id).pk
                details.save()
        else:
            messages.error(request, "Please correct the following errors:")
    else:
        # display the user's current details, if they exist
        try:
            user_profile = Profile.objects.get(user=user_id)
            location = user_profile.location or None
            max_dist = user_profile.max_distance or None
            data = {"location": location, "max_distance": max_dist}
            form = ProfileForm(data)
        except Profile.DoesNotExist:
            form = ProfileForm()

    args = {"active": "profile", "incomplete_profile": not complete, "form": form}
    args.update(csrf(request))
    return render(request, "accounts/profile.html", args)


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
