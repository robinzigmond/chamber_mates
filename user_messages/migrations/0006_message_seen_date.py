# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-28 20:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_messages', '0005_auto_20171022_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='seen_date',
            field=models.DateTimeField(null=True),
        ),
    ]
