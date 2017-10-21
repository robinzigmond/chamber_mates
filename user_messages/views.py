# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url=reverse_lazy("login"))
def messages(request):
    """
    A view for displaying the user's messages (inbox, with link to a message submission form,
    and to each message, and another to an outbox)
    """
    pass
