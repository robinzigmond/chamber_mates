# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Distance, Standard, Instrument, UserInstrument, Profile

# Register your models here.
admin.site.register(Distance)
admin.site.register(Standard)
admin.site.register(Instrument)
admin.site.register(UserInstrument)
admin.site.register(Profile)
