# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-20 20:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0005_auto_20171114_0031'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('desired_instruments', models.ManyToManyField(to='accounts.Instrument')),
                ('members', models.ManyToManyField(to='accounts.UserInstrument')),
            ],
        ),
    ]