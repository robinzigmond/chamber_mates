# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Message(models.Model):
    user_from = models.ForeignKey(User, related_name="user_from")
    user_to = models.ForeignKey(User, related_name="user_to")
    title = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    sender_deleted = models.BooleanField(default=False)
    receiver_deleted = models.BooleanField(default=False)
    sent_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.title
