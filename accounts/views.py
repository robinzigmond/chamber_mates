# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.gis.measure import Distance
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms import modelformset_factory
from django.template.context_processors import csrf
from django.db import IntegrityError
from django.conf import settings
from googlemaps import Client
from .forms import UserRegistrationForm, UserUpdateForm,ProfileForm, UserInstrumentForm
from .models import Profile, UserInstrument, Instrument


# helper function to look up a user's profile details. Used on both the "dashboard" page
# (where it applies to the logged-in user) and the generi "profiles" pages where users can
# browse the profiles of other users:
def get_profile_details(user):
    profile = get_object_or_404(User, pk=user.pk).profile
    instruments = UserInstrument.objects.filter(user=user.pk)
    
    # use google maps API to get a nicely formatted address string:
    point = profile.location
    # the database stores the latitude and longitude in the "co-ords" field of the Point Field object
    # - but in reverse order (longitute, then latitude). Since Google Maps expects the latitute to
    # be first, we reverse the tuple with ::-1
    results = Client(key=settings.GOOGLE_MAP_API_KEY).reverse_geocode(point.coords[::-1])
    # results is a list of dictionaries - the number is not possible to determine in advance
    # - representing geographical areas of decreasing specificity around the given point. Some
    # - but not all - will have a "formatted_address" key, and we will grab this data from the
    # first case where it actually exists, in order to get the most specific address possible.
    for item in results:
        try:
            place = item["formatted_address"]
            break
        except KeyError:
            continue
    # handle the possible case where no address can be found:
    if place is None:
        address_string = "Unknown"
    else:
        # remove first part of address - users will not want their full address to be publicly displayed!
        comma_location = place.find(",")
        address_string = place[comma_location+1:]
    return {"id": user, "location": address_string, "profile": profile, "instruments": instruments}


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
                messages.success(request, "You have successfully registered with Chamber Mates!")
                return redirect(reverse("edit_profile"))
            else:
                messages.error(request, "Oops, something went wrong! Please review your details and try again.")
        else:
            messages.error(request, """Sorry, something you entered wasn't right. Please correct
                                       the errors below and you'll be registered in no time!""")

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
def dashboard(request):
    try:
        profile = Profile.objects.get(user=request.user.pk)
    except Profile.DoesNotExist:
        messages.error(request, "Oops, something went wrong! Try completing your profile first!")
        return redirect(reverse("edit_profile"))

    args = {"active": "dashboard", "editable": True}
    args.update(get_profile_details(request.user))
    return render(request, "accounts/dashboard.html", args)


@login_required(login_url=reverse_lazy("login"))
def edit_profile(request):
    """
    view to handle the form for users to enter/edit their profile
    """
    user_id = request.user.pk
    try:
        user_profile = Profile.objects.get(user=user_id)
        num_instruments = UserInstrument.objects.filter(user=user_id).count()
        complete = user_profile.location and user_profile.max_distance and num_instruments > 0
        blank_forms = 1 if num_instruments==0 else 0
    except Profile.DoesNotExist:
        complete = False
        blank_forms = 1

    instrument_FormSet = modelformset_factory(UserInstrument, UserInstrumentForm,
                                              extra=blank_forms, can_delete=True)
    
    if request.method=="POST":
        baseform = UserUpdateForm(request.POST, user=request.user)
        profile_form = ProfileForm(request.POST)
        instrument_forms = instrument_FormSet(request.POST)
        
        if baseform.is_valid() and profile_form.is_valid() and instrument_forms.is_valid():
            # save the new email and/or password - but only if the user tried to change it!
            data = baseform.cleaned_data
            if baseform.fields["email"].has_changed(request.user.email, data["email"]):
                request.user.email = data["email"]
            if (baseform.fields["current_password"].has_changed(None, data["current_password"])
                or baseform.fields["new_password1"].has_changed(None, data["new_password1"])
                or baseform.fields["new_password2"].has_changed(None, data["new_password2"])):
                request.user.set_password(data["new_password1"])
                request.user.save()
            # save the non-instrument profile details (location and max_distance)
            details = profile_form.save(commit=False)
            details.user = request.user
            try:
                details.save()
            except IntegrityError:
                # this happens if the user already exists (because only one profile is allowed per user)
                # In other words, the user wants to update their profile. We allow this by specifying
                # the primary key when saving the model
                details.pk = Profile.objects.get(user=user_id).pk
                details.save()
            # now the instrument details
            instruments = instrument_forms.save(commit=False)
            for instr in instruments:
                instr.user = request.user
            instrument_forms.save()            
            verb = "updated" if complete else "completed"
            messages.success(request, "You have successfully "+verb+" your profile.")
            return redirect(reverse("dashboard"))

        else:
            messages.error(request, "Please correct the highlighted errors:")
    else:
        # display the user's current details, if they exist
        try:
            user_profile = Profile.objects.get(user=user_id)
            profile_form = ProfileForm(instance=user_profile)
            instrument_forms = instrument_FormSet(queryset=UserInstrument.objects.filter(user=user_id))
        except Profile.DoesNotExist:
            profile_form = ProfileForm()
            instrument_forms = instrument_FormSet(queryset=UserInstrument.objects.none())
        baseform = UserUpdateForm(initial={"email": request.user.email})

    if not complete:
        messages.success(request, """Please complete your profile with location and instrument information.
                                     We'll use this information to match you up with the players you want
                                     in your local area!""")

    args = {"active": "dashboard", "base_form": baseform, "profile_form": profile_form,
            "instrument_forms": instrument_forms}
    args.update(csrf(request))
    return render(request, "accounts/edit_profile.html", args)


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
                return redirect(reverse("dashboard"))
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Please correct the below errors and try again.")
    else:
        form = AuthenticationForm()
    
    args = {"active": "login", "form": form}
    args.update(csrf(request))

    return render(request, "accounts/login.html", args)


@login_required(login_url=reverse_lazy("login"))
def matches(request):
    """
    A view to handle displaying a list of all users matching the given user's search criteria
    in their profile
    """
    matches = {}
    # sample output of matches, for a user who plays violin and oboe. As a violinist they are
    # looking for a pianist and a cellist, and as an oboist they just want a pianist:
    # matches = {"violin": {"piano": ["Peter", "Jane", "John"], "cello": ["Bob"]},
    #            "oboe": {"piano": ["Lucy", "Robin"]}}

    profile = Profile.objects.get(user=request.user)
    max_dist = profile.max_distance.distance
    user_location = profile.location
    close_enough = User.objects.filter(profile__location__distance_lte=(user_location,
                                                                        Distance(mi=max_dist)))

    instruments_played = UserInstrument.objects.filter(user=request.user)

    for played in instruments_played:
        instruments_wanted = played.desired_instruments
        standards_wanted = played.accepted_standards.values("standard")
        for wanted in instruments_wanted.all():
            for user in close_enough:
                # we don't want to match anyone with themselves!
                if user == request.user:
                    continue
                if user.userinstrument_set.filter(instrument=wanted, 
                                                  standard__standard__in=standards_wanted).exists():
                    # we've found a match. Let's store these nicely in the nested "matches" dict
                    try:
                        instrument_matches = matches[played.instrument.instrument]
                        try:
                            wanted_matches = instrument_matches[wanted.instrument]
                            wanted_matches.append(user.username)
                        except KeyError:
                            instrument_matches[wanted.instrument] = [user.username]
                    except KeyError:
                        matches[played.instrument.instrument] = {wanted.instrument: [user.username]}

    return render(request, "accounts/matches.html", {"active": "dashboard", "matches": matches})


@login_required(login_url=reverse_lazy("login"))
def profiles(request, username):
    """
    A view to allow a specific user's public profile to be seen
    """
    user = get_object_or_404(User, username=username)
    args = {"active": "dashboard", "editable": False}
    args.update(get_profile_details(user))
    return render(request, "accounts/dashboard.html", args)
