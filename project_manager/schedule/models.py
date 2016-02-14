import datetime
import logging

from django.db import models

logger = logging.getLogger('project_manager')

class Project(models.Model):
    name = models.CharField(max_length=40, primary_key=True)

    def __str__(self):
        return str(self.name)


class Resource(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return str(self.name)

    def is_available(self, date):
        """Check whether this resource is available on the specified date.

        Currently we just assume that all resources are available on
        all weekdays.

        """
        assert isinstance(date, datetime.date)
        return date.weekday() in range(0, 5)


class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    orig_estimate = models.IntegerField()
    days_worked = models.IntegerField(default=0)
    estimate_remaining = models.IntegerField()
    resource = models.ForeignKey('Resource',
                                 on_delete=models.PROTECT,
                                 null=True)
    project = models.ForeignKey('Project',
                                on_delete=models.PROTECT,
                                null=True)

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

    def current_estimate(self):
        return self.days_worked + self.estimate_remaining

    def estimated_end_date(self, start_date):
        """Calculate when this task will end if it starts on the specified
        date, and if it takes the current estimated time.

        :param start_date: The date on which the task is to be
        started.

        """
        logger.debug("estimated_end_date(start_date=%s)",
                     start_date)
        
        end_date = start_date
        days_remaining = self.current_estimate()
        logger.debug("Estimated duration: %s", days_remaining)
        
        while days_remaining > 1 or (not self.resource.is_available(end_date)):
            if self.resource.is_available(end_date):
                logger.debug("Available on %s", end_date)
                days_remaining -= 1
            else:
                logger.debug("Not available on %s", end_date)
            end_date = end_date + datetime.timedelta(days=1)

        logger.debug("end date: %s", end_date)
        return end_date
