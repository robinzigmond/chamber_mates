# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-14 00:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_match'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name_plural': 'matches'},
        ),
        migrations.AddField(
            model_name='match',
            name='mark_new',
            field=models.BooleanField(default=True),
        ),
    ]
