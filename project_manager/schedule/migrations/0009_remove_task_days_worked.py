# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 22:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_resourceusage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='days_worked',
        ),
    ]