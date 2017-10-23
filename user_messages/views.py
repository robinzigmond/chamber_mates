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
    
    indices_to_delete = map(int, to_delete.split("-"))
    msgs = []

    # there are 2 separate loops here, one to fetch the messages to delete, the second one to delete them
    # it is not done in a single loop, because of the risk that the deletion would change the starting querySet,
    # and result in the wrong messages being deleted.
    # I do not know if this would actually happen, but the way below seems safer!

    for index in indices_to_delete:
        msgs.append(user_messages[index-1])
        # need to be careful to shift the index down by 1, because the "incoming" indices are 1-based, whereas
        # list indices are 0-based
        
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
