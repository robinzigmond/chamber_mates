# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserInstrument, Instrument

# Create your models here.
class Group(models.Model):
    """
    A model for the Groups which users can invite other users to - in order to meet
    and make music together
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    members = models.ManyToManyField(UserInstrument)
    desired_instruments = models.ManyToManyField(Instrument)

    def __unicode__(self):
        return self.name


class Invitation(models.Model):
    """
    A model to hold the information about invitations which are made for users to join
    a group
    """
    inviting_user = models.ForeignKey(User, related_name="inviting")
    invited_user = models.ForeignKey(User, related_name="invited")
    invited_instrument = models.ForeignKey(Instrument)
    group = models.ForeignKey(Group)

    class Meta:
        unique_together = (("invited_user", "group"),)

    def __unicode__(self):
        return "%s to play %s for %s" % (self.invited_user, self.invited_instrument, self.group)


class GroupThread(models.Model):
    """
    A model to describe a thread on a group's private forum
    """
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=200)
    started_by = models.ForeignKey(User)
    last_post = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.name


class GroupMessage(models.Model):
    """
    A model for individual posts to a group's private forum, which are organised into threads.
    """
    thread = models.ForeignKey(GroupThread)
    author = models.ForeignKey(User)
    message = models.TextField()
    posted_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.message[:30]
