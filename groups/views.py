# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.db import IntegrityError
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
def new_group(request, username=""):
    """
    A view to handle the form for starting a new group (via inviting a single other user)
    """
    if request.method == "POST":
        form = GroupSetupForm(data=request.POST, user=request.user)
        if form.is_valid():
            # create group and issue invitation (NB the group is created even if the user
            # declines the invitation - this is intentional)
            group = Group(name=request.POST.get("name"))
            try:
                group.save()
                # It should be allowable for the "desired_instruments" field to be left blank
                # - to allow for groups of just 2 users. Django internally requires the
                # ManyToManyField to be an iterable - otherwise an error is raised - but if
                # left blank the value included in the POST request is None. To avoid this
                # error, we manually set it to be the empty list.
                if request.POST.get("desired_instruments"):
                    group.desired_instruments = request.POST.get("desired_instruments")
                else:
                    group.desired_instruments = []

                my_instr = UserInstrument.objects.get(pk=request.POST.get("instrument"))
                group.members = [my_instr]
                group.save()
                
                invited_user = User.objects.get(username=request.POST.get("invited_user"))
                invited_instrument = UserInstrument.objects.get(pk=request.POST.get("invited_instrument"))
                Invitation.objects.create(inviting_user=request.user,
                                        invited_user=invited_user,
                                        invited_instrument=invited_instrument,
                                        group=group)
                messages.success(request, """Your new group %s has now been started!
                                             An invitation has been sent to %s
                                          """ % (request.POST.get("name"), 
                                                 request.POST.get("invited_user")))
                return redirect(reverse("my_groups"))
            
            except IntegrityError:
                # this happens if the user attempts to create a group with an already existing name
                # (since the name field has unique=True). Although this is a db error, it will make
                # most sense to the user to raise this as an error in the form itself
                form.add_error("name", "That group name is already taken!")

        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        form = GroupSetupForm(user=request.user, initial={"invited_user": username})
    
    args = {"active": "dashboard", "form": form}
    args.update(csrf(request))
    return render(request, "groups/new.html", args)


def group_detail(request, id):
    """
    A view to display the details of a group. The template will show different features
    depending on if the current user is a member of that group or not
    """
    group = get_object_or_404(Group, pk=id)
    
    # test for membership
    my_instruments = UserInstrument.objects.filter(user=request.user)
    member = False
    for instr in my_instruments:
        if group in Group.objects.filter(members__in=[instr]):
            member = True
            break
    
    invites = Invitation.objects.filter(group=group)
    
    return render(request, "groups/detail.html", {"group": group, "member": member,
                                                  "invites": invites})
