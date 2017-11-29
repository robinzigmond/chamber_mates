# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Group, Invitation, GroupThread, GroupMessage

# Register your models here.
admin.site.register(Group)
admin.site.register(Invitation)
admin.site.register(GroupThread)
admin.site.register(GroupMessage)
