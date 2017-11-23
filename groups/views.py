# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from accounts.models import UserInstrument
from .models import Group, Invitation
from .forms import GroupSetupForm

# Create your views here.
@login_required(login_url=reverse_lazy("login"))
def my_groups(request):
    """
    A view to fetch all groups which the requesting user is part of
    """
    instruments = UserInstrument.objects.filter(user=request.user)
    groups = []
    for instr in instruments:
        groups.extend(Group.objects.filter(members__in=[instr]))
    return render(request, "groups/my-groups.html", {"active": "dashboard", "groups": groups})


@login_required(login_url=reverse_lazy("login"))
def new_group(request):
    """
    A view to handle the form for starting a new group (via inviting a single other user)
    """
    if request.method == "POST":
        form = GroupSetupForm(data=request.POST, user=request.user)
        if form.is_valid():
            # create group and issue invitation (NB the group is created even if the user
            # declines the invitation - this is intentional)
            group = Group(name=request.POST.get("name"))
            group.save()
            group.desired_instruments=request.POST.get("desired_instruments")
            my_instr = UserInstrument.objects.get(user=request.user,
                                                  instrument=request.POST.get("instrument"))
            group.members = (my_instr, request.POST.get("invited_instrument"))
            group.save()
            
            Invitation.objects.create(inviting_user=request.user,
                                      invited_user=request.POST.get("invited_user"),
                                      invited_instrument=request.POST.get("invited_instrument"),
                                      group=group)
            messages.sucess(request, """Your new group %s has now been started! An invitation has been sent to
                            %s""" % (request.POST.get("name"), request.POST.get("invited_user").username))
            return redirect(reverse("my_groups"))

        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        form = GroupSetupForm(user=request.user)
    
    args = {"active": "dashboard", "form": form}
    args.update(csrf(request))
    return render(request, "groups/new.html", args)
