from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    orig_estimate = models.IntegerField()
    days_worked = models.IntegerField()
    estimate_remaining = models.IntegerField()


class Resource(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

