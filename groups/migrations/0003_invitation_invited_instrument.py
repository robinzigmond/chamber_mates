# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-23 00:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20171114_0031'),
        ('groups', '0002_invitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='invited_instrument',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.UserInstrument'),
            preserve_default=False,
        ),
    ]
