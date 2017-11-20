# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import UserInstrument
from .models import Group

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
