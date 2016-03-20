import datetime
import logging
import random
import string
import math

from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError

logger = logging.getLogger('project_manager')

def validate_half_day_granularity(value):
    if int(value * 2) != value * 2:
        raise ValidationError(
            "%(value)s is not rounded to whole or half day",
            params={'value': value}
        )

class Project(models.Model):
    name = models.CharField(max_length=40, primary_key=True)
    permalink = models.CharField(max_length=10, unique=True, null=False)

    def __str__(self):
        return str(self.name)

    def create_permalink(self):
        return ''.join(random.choice(string.ascii_lowercase
                                     + string.ascii_uppercase
                                     + string.digits)
                       for i in range(10))

    def save(self):
        if not self.permalink:
            self.permalink = self.create_permalink()

        super(Project, self).save()


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


class ResourceUsage(models.Model):
    resource = models.ForeignKey('Resource',
                                 on_delete=models.CASCADE,
                                 null=False)
    task = models.ForeignKey('Task',
                             on_delete=models.CASCADE,
                             null=False)
    date = models.DateField(null=False)
    used = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[validate_half_day_granularity])

    def __str__(self):
        return "Resource Usage ({resource}, {date})" \
            .format(resource=self.resource.name,
                    date=self.date)

class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)

    orig_estimate = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[validate_half_day_granularity])

    estimate_remaining = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[validate_half_day_granularity])

    resource = models.ForeignKey('Resource',
                                 on_delete=models.PROTECT,
                                 null=False)
    project = models.ForeignKey('Project',
                                on_delete=models.PROTECT,
                                null=False)

    @property
    def days_worked(self):
        return ResourceUsage.objects \
            .filter(task=self) \
            .aggregate(Sum('used')) \
            ["used__sum"] or 0

    @staticmethod
    def arrange_tasks():
        """Arrange the tasks so that they have sensible start and end dates
        given the resources that are assigned to them.

        :return: A list of dicts, which is messy but necessary for
        compatibility between the JSON output and the data needed to
        build SVG.

        """
        tasks = Task.objects.filter(estimate_remaining__gt=0).order_by('pk')

        result = []

        resource_available_dates = {}
        for resource in Resource.objects.all():
            resource_available_dates[resource.name] = datetime.datetime.now().date()

        last_tasks = {resource.name: None
                      for resource in Resource.objects.all()}

        for task in tasks:
            start_date = resource_available_dates[task.resource.name]
            end_date = task.estimated_end_date(start_date)
            result.append({'name': str(task.name),
                           'start_date': start_date,
                           'end_date': end_date,
                           'duration': task.estimate_remaining,
                           'depends_on': last_tasks[task.resource.name],
                           'resource': task.resource.name})

            resource_available_dates[task.resource.name] = end_date + datetime.timedelta(days=1)

            last_tasks[task.resource.name] = task.name

        return result

    def __str__(self):
        return self.name

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

        # We round up the work to the next whole day. We want to be
        # able to track half-days for counting gain and slip, but
        # accurately placing tasks on the plan in increments smaller
        # than a day is fiddly and not all that useful.
        days_remaining = math.ceil(self.estimate_remaining)

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


class Holiday(models.Model):
    resource = models.ForeignKey('Resource',
                                 on_delete=models.CASCADE,
                                 null=False)
    date = models.DateField(null=False)
