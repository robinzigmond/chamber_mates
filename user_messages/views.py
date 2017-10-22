# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Message

# Create your views here.
@login_required(login_url=reverse_lazy("login"))
def inbox(request):
    """
    A view for displaying the user's message inbox
    """
    user_messages = Message.objects.filter(user_to=request.user)
    return render(request, "user_messages/messages.html", {"active": "dashboard", "view": "inbox",
                                                  "usermessages": user_messages})


@login_required(login_url=reverse_lazy("login"))
def outbox(request):
    """
    A view for displaying the user's sent messages
    """
    user_messages = Message.objects.filter(user_from=request.user)
    return render(request, "user_messages/messages.html", {"active": "dashboard", "view": "outbox",
                                                  "usermessages": user_messages})
