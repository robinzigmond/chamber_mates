# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.db import IntegrityError
from accounts.models import UserInstrument, Instrument
from .models import Group, Invitation
from .forms import GroupSetupForm, InvitationForm, DecideOnInvitation

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
    invited_groups = Group.objects.filter(invitation__invited_user__in=[request.user]).distinct()
    return render(request, "groups/my-groups.html", {"active": "dashboard", "groups": groups,
                                                     "invited": invited_groups})


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
            group = Group(name=form.cleaned_data["name"])
            try:
                group.save()
                # It should be allowable for the "desired_instruments" field to be left blank
                # - to allow for groups of just 2 users. Django internally requires the
                # ManyToManyField to be an iterable - otherwise an error is raised - but if
                # left blank the value included in the POST request is None. To avoid this
                # error, we manually set it to be the empty list.
                if request.POST.get("desired_instruments"):
                    group.desired_instruments = form.cleaned_data["desired_instruments"]
                else:
                    group.desired_instruments = []

                my_instr = UserInstrument.objects.get(pk=form.cleaned_data["instrument"])
                group.members = [my_instr]
                group.save()
                
                invited_user = User.objects.get(username=form.cleaned_data["invited_user"])
                invited_instrument = UserInstrument.objects.get(pk=request.POST.get("invited_instrument")) \
                                                                .instrument
                Invitation.objects.create(inviting_user=request.user,
                                        invited_user=invited_user,
                                        invited_instrument=invited_instrument,
                                        group=group)
                messages.success(request, """Your new group %s has now been started!
                                             An invitation has been sent to %s
                                          """ % (form.cleaned_data["name"], 
                                                 form.cleaned_data["invited_user"]))
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


@login_required(login_url=reverse_lazy("login"))
def invite_for_instrument(request, group_id, instr_name):
    """
    A view to invite a user to an existing group, to play a specific instrument
    """
    group = get_object_or_404(Group, pk=group_id)
    instrument = get_object_or_404(Instrument, instrument=instr_name)
    # if the current user is not a member of the group, we don't allow them to
    # access the form.
    # If the group does not desire the instrument requested, return to the group page
    # with an explanatory error message.
    try:
        user_instrument = UserInstrument.objects.get(user=request.user,
                                                     group__in=[group])
        if instrument not in group.desired_instruments.all():
            messages.error(request, "The %s group isn't looking for a %s player!" %(group.name,
                                                                                    instrument.instrument))
            return redirect(reverse("group", kwargs={"id": group_id}))

    except UserInstrument.DoesNotExist:
        raise PermissionDenied

    if request.method == "POST":
        form = InvitationForm(request.POST, instr=instr_name)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.inviting_user = request.user
            invitation.invited_user = User.objects.get(username=request.POST.get("invited_user"))
            # display an error message if you are trying to invite someone already in the group
            if group in Group.objects.filter(members__user__in=[invitation.invited_user]):
                form.add_error("invited_user", "%s is already in this group!" \
                              %request.POST.get("invited_user"))                
            else:
                try:
                    invitation.save()
                    messages.success(request,
                                    "Your invitation was sent to %s" %request.POST.get("invited_user"))
                    return redirect(reverse("group", kwargs={"id": group_id}))
                except IntegrityError:
                    # This happens when the uniqueness constraint is violated - that is,
                    # you try to invite someone who has already been invited to the same
                    # group
                    form.add_error("invited_user", "%s has already been invited to join this group!" \
                                    %request.POST.get("invited_user"))
        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        form = InvitationForm(initial={"group": group, "invited_instrument": instrument},
                              instr=instr_name)
    
    args = {"active": "dashboard", "form": form, "group": group.name,
            "instrument": instr_name}
    args.update(csrf(request))
    return render(request, "groups/specific-invite.html", args)


@login_required(login_url=reverse_lazy("login"))
def group_detail(request, id):
    """
    A view to display the details of a group. The template will show different features
    depending on if the current user is a member of that group or not
    """
    group = get_object_or_404(Group, pk=id)
    
    # test for membership
    member = False
    my_instruments = UserInstrument.objects.filter(user=request.user)
    for instr in my_instruments:
        if group in Group.objects.filter(members__in=[instr]):
            member = True
            break
    
    invites = Invitation.objects.filter(group=group)
    my_invites = invites.filter(invited_user=request.user)
    other_invites = invites.exclude(invited_user=request.user)
    mini_form = DecideOnInvitation()
    
    args = {"active": "dashboard", "group": group, "member": member,
            "my_invites": my_invites, "other_invites": other_invites,"mini_form": mini_form}
    args.update(csrf(request))
    return render(request, "groups/detail.html", args)
