from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    orig_estimate = models.IntegerField()
    days_worked = models.IntegerField(default=0)
    estimate_remaining = models.IntegerField()

    def save(self, *args, **kwargs):
        """Override the behaviour so that the estimate remaining is set to the
        original estimate when the task is first created.

        """
        if self.estimate_remaining is None:
            self.estimate_remaining = self.orig_estimate

        super(Task, self).save(*args, **kwargs)

    def gain(self):
        return self.orig_estimate - (self.days_worked +
                                     self.estimate_remaining)


class Resource(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

