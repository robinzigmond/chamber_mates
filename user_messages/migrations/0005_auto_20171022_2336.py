# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-22 22:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_messages', '0004_auto_20171022_2246'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='received_deleted',
            new_name='receiver_deleted',
        ),
    ]
