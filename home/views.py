# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "home/home.html", {"active": "home"})


def why(request):
    return render(request,"home/why.html", {"active": "why"})
