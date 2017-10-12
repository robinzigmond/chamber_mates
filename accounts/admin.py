# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.gis.db import models
from .models import Distance, Standard, Instrument, UserInstrument, Profile
from mapwidgets.widgets import GooglePointFieldWidget

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }


admin.site.register(Distance)
admin.site.register(Standard)
admin.site.register(Instrument)
admin.site.register(UserInstrument)
admin.site.register(Profile, ProfileAdmin)
