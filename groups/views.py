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
from django.http import Http404
from django.utils import timezone
from accounts.models import UserInstrument, Instrument
from .models import Group, Invitation, GroupThread, GroupMessage
from .forms import GroupSetupForm, InvitationForm, DecideOnInvitation, GroupUpdateForm, GroupMessageForm


def is_member(user, group):
    """
    In a couple of view functions below, it is required to check whether a given user
    is a member of a particular group. Since the group object defines its members field
    via the UserInstrument model rather than the User model, this takes a number of lines
    of code and so has been factored out to a separate function to avoid repetition.
    """
    instruments_played = UserInstrument.objects.filter(user=user)
    for instr in instruments_played:
        if group in Group.objects.filter(members__in=[instr]):
            return True
    return False


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
        form.order_fields(["name", "instrument", "invited_user", "desired_instruments"])
        if form.is_valid():
            # create group and issue invitation (NB the group is created even if the user
            # declines the invitation - this is intentional)
            group = Group(name=form.cleaned_data["name"])
            try:
                invited_user = User.objects.get(username=form.cleaned_data["invited_user"])
                if invited_user == request.user:
                    form.add_error("name", "You can't invite yourself!")
                else:
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
        form.order_fields(["name", "instrument", "invited_user", "desired_instruments"])
    
    args = {"active": "dashboard", "form": form}
    args.update(csrf(request))
    return render(request, "groups/new.html", args)


@login_required(login_url=reverse_lazy("login"))
def specific_invite(request, group_id, instr_name=None, user_id=None):
    """
    A view to invite a user to an existing group, to play a specific instrument
    """
    group = get_object_or_404(Group, pk=group_id)
    if not is_member(request.user, group):
        raise PermissionDenied

    if instr_name:
        instrument = get_object_or_404(Instrument, instrument=instr_name)
        # If the group does not desire the instrument requested, return to the group page
        # with an explanatory error message.
        if instrument not in group.desired_instruments.all():
            messages.error(request, "The %s group isn't looking for a %s player!" %(group.name,
                                                                                    instrument.instrument))
        return redirect(reverse("group", kwargs={"id": group_id}))

    if user_id:
        user = get_object_or_404(User, pk=user_id)

    # determine fields to exclude from form, depending on the circumstances this view is called:
    exclusions = ["group"]
    if instr_name:
        exclusions.append("invited_instrument")
    if user_id:
        exclusions.append("invited_user")

    if request.method == "POST":
        form = InvitationForm(request.POST, instr=instr_name, exclude=exclusions)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.inviting_user = request.user
            invitation.group = Group.objects.get(pk=group_id)
            if instrument:
                invitation.invited_instrument = instrument
            else:
                invitation.invited_instrument = Instrument.objects.get(instrument=instr_name)
            if user:
                invitation.invited_user = user
            else:
                invitation.invited_user = User.objects.get(username=request.POST.get("invited_user"))
            # display an error message if you are trying to invite someone already in the group
            if group in Group.objects.filter(members__user__in=[invitation.invited_user]):
                form.add_error("invited_user", "%s is already in this group!" \
                               %invitation.invited_user.username)                
            else:
                try:
                    invitation.save()
                    messages.success(request,
                                    "Your invitation was sent to %s" %invitation.invited_user.username)
                    return redirect(reverse("group", kwargs={"id": group_id}))
                except IntegrityError:
                    # This happens when the uniqueness constraint is violated - that is,
                    # you try to invite someone who has already been invited to the same
                    # group
                    form.add_error("invited_user", "%s has already been invited to join this group!" \
                                    %invitation.invited_user.username)
        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        form = InvitationForm(instr=instr_name, exclude=exclusions)
    
    args = {"active": "dashboard", "form": form, "group": group,
            "instrument": instr_name, "user": user}
    args.update(csrf(request))
    return render(request, "groups/specific-invite.html", args)


@login_required(login_url=reverse_lazy("login"))
def group_detail(request, id):
    """
    A view to display the details of a group. The template will show different features
    depending on if the current user is a member of that group or not.
    It also can include a "mini-form" for users invited to that group to select if they
    accept the invitation or not.
    """
    group = get_object_or_404(Group, pk=id)
    invites = Invitation.objects.filter(group=group)
    my_invites = invites.filter(invited_user=request.user)
    other_invites = invites.exclude(invited_user=request.user)
    threads = GroupThread.objects.filter(group=group).order_by("-last_post")

    if request.method == "POST":
        mini_form = DecideOnInvitation(request.POST)
        if mini_form.is_valid():
            invite_to_answer = my_invites[0]
            invited_instr = UserInstrument.objects.get(user=request.user,
                                                       instrument=invite_to_answer.invited_instrument)
            # there will be only 1 invite now that the db enforces at most 1 invite per user
            # per group
            invite_to_answer.delete()
            if mini_form.cleaned_data["accept_or_decline"] == "accept":
                group.members.add(invited_instr)
                messages.success(request,
                                 "You are now a member of the group %s!" %group.name)
            else:
                messages.success(request,
                                 "You have declined the invitation to join the group %s!" %group.name)
                # add the instrument back on to the group's desired instrument list,
                # if it isn't already there
                if invited_instr not in group.desired_instruments.all():
                    group.desired_instruments.add(invited_instr.instrument)

                return redirect(reverse("my_groups"))
        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        mini_form = DecideOnInvitation()

    args = {"active": "dashboard", "group": group, "member": is_member(request.user, group),
            "my_invites": my_invites, "other_invites": other_invites,
            "threads": threads, "mini_form": mini_form}
    args.update(csrf(request))
    return render(request, "groups/detail.html", args)


@login_required(login_url=reverse_lazy("login"))
def update_group(request, id):
    """
    A view to handle the form for updating group information.
    """
    group = get_object_or_404(Group, pk=id)
    if not is_member(request.user, group):
        raise PermissionDenied
   
    if request.method == "POST":
        form = GroupUpdateForm(request.POST)
        if form.is_valid():
            group.name = form.cleaned_data["name"]
            group.desired_instruments = form.cleaned_data["desired_instruments"]
            group.save()
            messages.success(request, "The details for group %s have been updated!" %group.name)
            return redirect(reverse("group", kwargs={"id": id}))
        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        form = GroupUpdateForm({"name": group.name,
                                "desired_instruments": group.desired_instruments.all()})

    args = {"active": "dashboard", "form": form,"group": group}
    args.update(csrf(request))
    return render(request, "groups/update.html", args)


@login_required(login_url=reverse_lazy("login"))
def new_thread(request, group_id):
    """
    A view to handle the form for starting a new thread on a group's forum/message-board
    """
    group = get_object_or_404(Group, pk=group_id)
    if not is_member(request.user, group):
        raise PermissionDenied
    
    if request.method == "POST":
        form = GroupMessageForm(request.POST, new_thread=True)
        form.order_fields(["name", "message"])
        if form.is_valid():
            new_thread = GroupThread.objects.create(group=group, name=form.cleaned_data["name"],
                                       started_by=request.user)
            message = form.save(commit=False)
            message.thread = new_thread
            message.author = request.user
            message.save()
            messages.success(request, "You have started the conversation thread %s" %new_thread.name)
            return redirect(reverse("view_thread", kwargs={"group_id": group_id,
                                                           "thread_id": new_thread.pk}))
        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        form = GroupMessageForm(new_thread=True)
        form.order_fields(["name", "message"])
    
    args = {"active": "dashboard", "form": form, "group": group}
    args.update(csrf(request))
    return render(request, "groups/new_thread.html", args)


@login_required(login_url=reverse_lazy("login"))
def view_thread(request, group_id, thread_id):
    """
    A view to display the messages in a given group thread
    """
    group = get_object_or_404(Group, pk=group_id)
    if not is_member(request.user, group):
        raise PermissionDenied
    thread = get_object_or_404(GroupThread, pk=thread_id)
    if thread.group != group:
        raise Http404("That thread doesn't belong to this group!")
    thread_messages = thread.groupmessage_set.order_by("posted_date")

    if request.method == "POST":
        form = GroupMessageForm(request.POST, new_thread=False)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.thread = thread
            new_message.author = request.user
            new_message.save()
            # update "last post" property of thread!
            thread.last_post = timezone.now()
            thread.save()
            # no need to redirect, as want to view the new message as part of the thread
            # but do want to empty the contents of the form!
            form = GroupMessageForm(new_thread=False)
        else:
            messages.error(request, "Please correct the indicated errors and try again")
    else:
        form = GroupMessageForm(new_thread=False)
    
    args = {"active": "dashboard", "thread": thread,
            "thread_messages": thread_messages, "form": form}
    args.update(csrf(request))
    return render(request, "groups/thread.html", args)


@login_required(login_url=reverse_lazy("login"))
def delete(request, group_id, thread_id, msg_id):
    """
    A view to delete a message from a group forum thread. Access only allowed if the
    message is the user's own!
    """

    # get the necessary "admin" out of the way first!
    # This is unnecessary for normal use of the site, but prevents anything untoward happening
    # if users play around with the urls manually.
    group = get_object_or_404(Group, pk=group_id)
    if not is_member(request.user, group):
        raise PermissionDenied
    thread = get_object_or_404(GroupThread, pk=thread_id)
    if thread.group != group:
        raise Http404("That thread doesn't belong to this group!")
    msg = get_object_or_404(GroupMessage, pk=msg_id)
    if msg.thread != thread:
        raise Http404("That message isn't from the thread requested!")
    if msg.author != request.user:
        raise PermissionDenied
    
    # if everything checks out, then we can just delete the object and redirect the user
    msg.delete()
    messages.success(request, "Your message was deleted!")

    # if it's the last message in the thread, then delete the thread too
    if thread.groupmessage_set.count() == 0:
        thread.delete()
        return redirect(reverse("group", kwargs={"id": group_id}))
    else:
        return redirect(reverse("view_thread", kwargs={"group_id": group_id, "thread_id": thread_id}))


@login_required(login_url=reverse_lazy("login"))
def add_invitation(request, group_id, user_id):
    """
    A view to handle the situation where a user invites a specific user to a specific
    one of their groups, via that user's profile page.
    """
    group = get_object_or_404(Group, pk=group_id)
    if not is_member(request.user, group):
        raise PermissionDenied
    user_to_invite = get_object_or_404(User, pk=user_id)
    # get all instruments which that user plays AND are desired by the group
    their_instruments = UserInstrument.objects.filter(user=user_to_invite)
    possible_to_invite = group.desired_instruments.filter(user_plays__in=their_instruments)
    # check how many instruments are possible:
    instr_count = possible_to_invite.count()
    if instr_count == 0:
        # this isn't possible from the normal user interface, but is from the user messing
        # with urls manually. Give an error message and redirect the user to their dashboard
        messages.error(request, "You tried to issue an invalid invitation!")
        return redirect(reverse("dashboard"))
    elif instr_count == 1:
        # simply send an invitation and send the user to the relevant group's page (so they
        # can see that the invitation was successful)
        try:
            Invitation.objects.create(inviting_user=request.user,
                                    invited_user=user_to_invite,
                                    invited_instrument=possible_to_invite[0],
                                    group=group)
            return redirect(reverse("group", kwargs={"id": group_id}))
        except IntegrityError:
            # in case an invitation has already been sent
            messages.error(request,
            "%s has already been invited to the group %s!" %(user_to_invite.username, group.name))
            return redirect(reverse("dashboard"))
    else:
        # there is more than one possible instrument. Redirect to the appropriate pre-populated
        # invitation form so the user can choose the instrument
        return redirect(reverse("invite_for_user", kwargs={"group_id": group_id, "user_id": user_id}))
