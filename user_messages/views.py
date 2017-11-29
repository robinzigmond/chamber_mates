# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template.context_processors import csrf
from django.utils import timezone
from .models import Message
from .forms import MessageForm

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
    return render(request, "user_messages/messages.html", {"active": "dashboard", "view": "sent",
                                                           "usermessages": user_messages})


@login_required(login_url=reverse_lazy("login"))
def delete(request, to_delete, view):
    """
    view to handle the deleting of messages. Note that deletion is "one-sided" - a user can delete a message
    from their inbox without it disappearing from the receiver's outbox. This is what the sender_deleted and
    receiver_deleted fields are for. The message is only actually deleted when both these fields are set to
    True.
    """
    if view not in ["inbox", "sent"]:
        raise Http404("Page not found")

    if view == "inbox":
        user_messages = Message.objects.filter(user_to=request.user, receiver_deleted=False).order_by("-sent_date")
    else:
        user_messages = Message.objects.filter(user_from=request.user, sender_deleted=False).order_by("-sent_date")
    
    ids_to_delete = map(int, to_delete.split("-"))
    msgs = []

    for key in ids_to_delete:
        try:
            msg = user_messages.get(pk=key)
            msgs.append(msg)
        except Message.DoesNotExist:
            # this exception should not arise during "normal" use - but if for some reason a user
            # enters one of the "delete" URLs manually, we need to handle the case where the messages
            # does not exist.
            # This also serves the very important purpose of preventing maliciously deleting another
            # user's messages by typing the URL to delet it directly. (Since the messages have already
            # been filtered into the "legal" ones, any such attempt will raise this DoesNotExist error.)
            messages.error(request, "Unable to delete the specified messages")
            return redirect(reverse(view))

        
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


@login_required(login_url=reverse_lazy("login"))
def view_msg(request, view, msg_id):
    """
    View to fetch and display a single post
    """
    if view not in ["inbox", "sent"]:
        raise Http404("Page not found")

    msg = get_object_or_404(Message, pk=msg_id)

    # make sure the user is allowed to see the message:
    if msg.user_to != request.user and msg.user_from != request.user:
        raise PermissionDenied
    
    # mark the message as read, if the current user is the receiver:
    if msg.user_to == request.user:
        msg.seen = True
        msg.seen_date = timezone.now()
        msg.save()

    # the main reason for passing the "view" to the template is so that it can be passed back to
    # the "delete" view when deleting the post. The delete view, in turn, only requires this so that
    # when accessed from the inbox/outbox it knows where to direct the user to.
    # It also allows the "return to inbox/outbox" button to know which text it should have.
    return render(request, "user_messages/view_msg.html", {"active": "dashboard", "view": view, "msg": msg})


@login_required(login_url=reverse_lazy("login"))
def new_msg(request, to=None):
    """
    View to handle the form for writing/sending a new message
    """
    if to:
        user_to = get_object_or_404(User, username=to).username
        focus_field = "title"
    else:
        user_to = None
        focus_field = "user_to"
    if request.method == "POST":
        form = MessageForm(request.POST)
        form.order_fields(["user_to", "title", "message"])
        if form.is_valid():
            message = form.save(commit=False)
            message.user_from = request.user
            message.user_to = form.cleaned_data["user_to"]
            message.save()
            messages.success(request, "Your message was sent to "+message.user_to.username+" !")
            return redirect(reverse("inbox"))
        else:
            messages.error(request, "Please correct the highlighted errors:")

    else:
        form = MessageForm(initial={"user_to": user_to})
        form.order_fields(["user_to", "title", "message"])

    args = {"active": "dashboard", "form": form, "focus_field": focus_field}
    args.update(csrf(request))
    return render(request, "user_messages/new_msg.html", args)


@login_required(login_url=reverse_lazy("login"))
def reply(request, reply_to):
    """
    Modified version of the "new post" view to handle replying to a specific message
    """
    if request.method == "POST":
        # form handling is EXACTLY as for any other new post:
        form = MessageForm(request.POST)
        form.order_fields(["user_to", "title", "message"])
        if form.is_valid():
            message = form.save(commit=False)
            message.user_from = request.user
            message.user_to = form.cleaned_data["user_to"]
            message.save()
            messages.success(request, "Your message was sent to "+message.user_to.username+" !")
            return redirect(reverse("inbox"))
        else:
            messages.error(request, "Please correct the highlighted errors:")

    else:
        # we prepopulate the form with the user, title and previous message:
        msg = get_object_or_404(Message, pk=reply_to)
        if msg.user_to != request.user and msg.user_from != request.user:
            raise PermissionDenied    
        form = MessageForm(initial={"user_to": msg.user_from.username,
                                    "title": "RE: "+msg.title,
                                    "message": "\n\n----------Replying to----------\n"+msg.message})
        form.order_fields(["user_to", "title", "message"])

    args = {"active": "dashboard", "form": form, "focus_field": "message"}
    args.update(csrf(request))
    return render(request, "user_messages/new_msg.html", args)
