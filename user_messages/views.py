# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Message

# Create your views here.
@login_required(login_url=reverse_lazy("login"))
def inbox(request):
    """
    A view for displaying the user's message inbox
    """
    user_messages = Message.objects.filter(user_to=request.user, receiver_deleted=False).order_by("-sent_date")
    return render(request, "user_messages/messages.html", {"active": "dashboard", "view": "inbox",
                                                  "usermessages": user_messages})


@login_required(login_url=reverse_lazy("login"))
def outbox(request):
    """
    A view for displaying the user's sent messages
    """
    user_messages = Message.objects.filter(user_from=request.user, sender_deleted=False).order_by("-sent_date")
    return render(request, "user_messages/messages.html", {"active": "dashboard", "view": "outbox",
                                                           "usermessages": user_messages})


@login_required(login_url=reverse_lazy("login"))
def delete(request, to_delete, view):
    """
    view to handle the deleting of messages. Note that deletion is "one-sided" - a user can delete a message
    from their inbox without it disappearing from the receiver's outbox. This is what the sender_deleted and
    receiver_deleted fields are for. The message is only actually deleted when both these fields are set to
    True.
    """
    if view not in ["inbox", "outbox"]:
        raise Http404("Page not found")

    if view == "inbox":
        user_messages = Message.objects.filter(user_to=request.user, receiver_deleted=False).order_by("-sent_date")
    else:
        user_messages = Message.objects.filter(user_from=request.user, sender_deleted=False).order_by("-sent_date")
    
    ids_to_delete = map(int, to_delete.split("-"))
    msgs = []

    for key in ids_to_delete:
        msgs.append(user_messages.get(pk=key))

        
    for msg in msgs:
        if view=="inbox":
            msg.receiver_deleted=True
            if msg.sender_deleted:
                msg.delete()
            else:
                msg.save()
        else:
            msg.sender_deleted=True
            if msg.receiver_deleted:
                msg.delete()
            else:
                msg.save()

    if len(msgs)>1:
        success_str = "Messages successfully deleted!"
    else:
        success_str = "Message successfully deleted!"
    messages.success(request, success_str)
    return redirect(reverse(view))
