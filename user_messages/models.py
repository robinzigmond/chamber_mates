# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Message(models.Model):
    user_from = models.ForeignKey(User, related_name="user_from")
    user_to = models.ForeignKey(User, related_name="user_to")
    message = models.TextField()
    seen = models.BooleanField(default=False)

    def __unicode__(self):
        return self.message[:30]
