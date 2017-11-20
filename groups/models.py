# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserInstrument, Instrument

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(UserInstrument)
    desired_instruments = models.ManyToManyField(Instrument)

    def __unicode__(self):
        return self.name

class Invitation(models.Model):
    inviting_user = models.ForeignKey(User, related_name="inviting")
    invited_user = models.ForeignKey(User, related_name="invited")
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return "%s for %s" % (self.invited_user, self.group)
