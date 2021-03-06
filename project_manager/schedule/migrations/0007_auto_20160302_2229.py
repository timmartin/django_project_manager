# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-02 22:29
from __future__ import unicode_literals

from django.db import migrations, models
import schedule.models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0006_project_permalink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='permalink',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='days_worked',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=4, validators=[schedule.models.validate_half_day_granularity]),
        ),
        migrations.AlterField(
            model_name='task',
            name='estimate_remaining',
            field=models.DecimalField(decimal_places=1, max_digits=4, validators=[schedule.models.validate_half_day_granularity]),
        ),
        migrations.AlterField(
            model_name='task',
            name='orig_estimate',
            field=models.DecimalField(decimal_places=1, max_digits=4, validators=[schedule.models.validate_half_day_granularity]),
        ),
    ]
