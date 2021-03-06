# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth.models import User

# Create your models here.
class Distance(models.Model):
    """
    A very simple model, which holds just single numeric values for the default values the user will
    select from when choosing the "max_distance" value. These will be set in the Django admin (and
    refer to miles) - the possible values will be 5, 10, 20, 30 and 50.
    """
    distance = models.SmallIntegerField()

    def __unicode__(self):
        return str(self.distance)


class Profile(models.Model):
    """
    This model will contain all of a user's key information, apart from what is required for
    authentication (username, password and email). The fields are:
    - description (a text field the user can fill in giving personal or other information, tp
    describe to other users what they are looking for)
    - location
    - max_distance: An integer denoting the maximum distance (in miles) from their location
    that a user wishes to go to make contact with another user. Uses one of the values in
    the Distances model.
    We also of course use a OneToOneField to link it to a specific user!
    """
    user = models.OneToOneField(User)
    description = models.CharField(max_length=500, null=True, blank=True)
    location = models.PointField()
    max_distance = models.ForeignKey(Distance)

    def __unicode__(self):
        return self.user.username


class Instrument(models.Model):
    """
    Similar to the Distance model above, this will simple store a list of instrument names
    that a user can select from.
    """
    instrument = models.CharField(max_length=20)

    def __unicode__(self):
        return self.instrument


class Standard(models.Model):
    """
    And again, to store the choices that will be listed for the user to choose between
    when selecting their approximate standard on each instrument they play.
    """
    standard = models.CharField(max_length=200)

    def __unicode__(self):
        return self.standard


class UserInstrument(models.Model):
    """
    This model is used to store the information on the instruments the user plays.
    For each instrument, it allows the user to select what other instruments they are
    looking to join up with, and what standard(s) they will accept from other players.
    """
    user = models.ForeignKey(User)
    instrument = models.ForeignKey(Instrument, related_name="user_plays")
    standard = models.ForeignKey(Standard, related_name="user_plays")
    desired_instruments = models.ManyToManyField(Instrument, related_name="user_wanting")
    accepted_standards = models.ManyToManyField(Standard, related_name="user_wanting")

    def __unicode__(self):
        return "%s, %s" %(self.user.username, self.instrument)


class Match(models.Model):
    """
    This model is used to keep track of all matches between users
    """
    requesting_user = models.ForeignKey(User, related_name="match_looked_for")
    found_user = models.ForeignKey(User, related_name="match_found")
    requesting_instrument = models.ForeignKey(UserInstrument, related_name="match_looked_for")
    found_instrument = models.ForeignKey(UserInstrument, related_name="match_found")
    # 2 boolean fields to control the "status" of a match. "Known" is used to determine whether
    # to inform the user whether there are any new matches, while "mark_new" is used to display
    # the new matches in a more eye-catching way in the matches template.
    # 2 separate fields are needed because, when the matches page is viewed, any "unknown" matches
    # need to be marked as known, but without affecting their display as "new" matches.
    known = models.BooleanField(default=False)
    mark_new = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "matches"

    def __unicode__(self):
        return "%s-%s for %s-%s" %(self.found_user.username, self.found_instrument.instrument,
                                   self.requesting_user.username, self.requesting_instrument.instrument)
