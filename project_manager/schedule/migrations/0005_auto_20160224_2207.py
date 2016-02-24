# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 22:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20160214_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.Project'),
        ),
        migrations.AlterField(
            model_name='task',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schedule.Resource'),
        ),
    ]
