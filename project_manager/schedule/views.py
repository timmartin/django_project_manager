import datetime
import logging
import io

from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from .models import Project, Task, Resource, ResourceUsage
from .forms import TaskCreateForm, TaskEditForm

import gantt

logger = logging.getLogger('project_manager')

@login_required
def index(request):
    tasks = Task.objects.filter(estimate_remaining__gt=0).order_by('pk')
    completed_tasks = Task.objects.filter(estimate_remaining=0).order_by('pk')

    context = {'tasks': tasks,
               'completed_tasks': completed_tasks,
               'project': Project.objects.first(),
               'resources': Resource.objects.all()}
    return render(request, 'schedule/index.html', context)


@login_required
def resource_weekly_usage(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)

    start_date = datetime.date.today()
    start_date = start_date - datetime.timedelta(days=start_date.weekday())

    end_date = start_date + datetime.timedelta(days=5)

    usages = ResourceUsage.objects \
                          .filter(resource=resource,
                                  date__gte=start_date,
                                  date__lte=end_date) \
                          .order_by('date')

    usage_lookup = {}

    tasks = list(Task.objects.filter(resource=resource))

    for usage in usages:
        offset = (usage.date - start_date).days
        logger.debug("Processing %s, offset=%d", usage, offset)

        if usage.task in tasks:
            css_class = "task_color%d" % tasks.index(usage.task)
        else:
            logger.debug("%s not in %s",
                         usage.task,
                         tasks)
            css_class = None

        if offset in usage_lookup:
            logger.debug("AM already exists, adding PM")
            usage_lookup[offset]['pm'] = {'pk': usage.task.pk,
                                          'label': usage.task.name,
                                          'css_class': css_class}
        else:
            logger.debug("Adding to AM")
            usage_lookup[offset] = {}
            usage_lookup[offset]['am'] = {'pk': usage.task.pk,
                                          'label': usage.task.name,
                                          'css_class': css_class}

            if usage.used > 0.5:
                logger.debug("Extending to PM")
                usage_lookup[offset]['pm'] = {'pk': usage.task.pk,
                                              'label': usage.task.name,
                                              'css_class' : css_class}

    context = {'resource': resource,
               'tasks': tasks,
               'start_date': start_date,
               'usage_lookup': usage_lookup}

    return render(request, 'schedule/resource_weekly_usage.html', context)


@login_required
def resource_usage_update(request):

    resource = get_object_or_404(Resource, pk=request.POST['resource'])

    start_date = datetime.datetime.strptime(request.POST['start_date'],
                                            '%Y-%m-%d') \
                                  .date()

    with transaction.atomic():
        for day in range(5):
            current_date = start_date + datetime.timedelta(days=day)

            usage_to_delete = ResourceUsage.objects.filter(resource=resource,
                                                           date=current_date)
            for usage in usage_to_delete:
                usage.task.estimate_remaining += usage.used
                usage.task.save()
            usage_to_delete.delete()

            am_task = request.POST.get('days[AM][%d]' % day, '')
            pm_task = request.POST.get('days[PM][%d]' % day, '')

            if am_task != '':
                am_task = Task.objects.get(pk=int(am_task))
            else:
                am_task = None

            if pm_task != '':
                pm_task = Task.objects.get(pk=int(pm_task))
            else:
                pm_task = None

            if (am_task == pm_task) and (am_task is not None):
                usage = ResourceUsage(resource=resource,
                                      task=am_task,
                                      date=current_date,
                                      used=1)
                usage.save()

                am_task.estimate_remaining -= 1
                am_task.save()
            else:
                if am_task:
                    am_usage = ResourceUsage(resource=resource,
                                             task=am_task,
                                             date=current_date,
                                             used=0.5)
                    am_usage.save()

                    am_task.estimate_remaining -= Decimal(0.5)
                    am_task.save()

                if pm_task:
                    pm_usage = ResourceUsage(resource=resource,
                                             task=pm_task,
                                             date=current_date,
                                             used=0.5)
                    pm_usage.save()

                    pm_task.estimate_remaining -= Decimal(0.5)
                    pm_task.save()

    return HttpResponseRedirect("/schedule/")


class TaskEdit(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['name', 'resource', 'estimate_remaining']
    form = TaskEditForm
    template_name = "schedule/edit_task.html"

    success_url = reverse_lazy('schedule:index')


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['name', 'orig_estimate', 'resource', 'project']
    form = TaskCreateForm

    success_url = reverse_lazy('schedule:index')


@login_required
def gantt_json(request):
    return JsonResponse(Task.arrange_tasks(), safe=False)


def gantt_svg_permalink(request, permalink):
    """Get the Gantt chart as an SVG, when a permalink has been
    specified. This is allowed to be accessed without a login, to make
    it easier to embed the permalink in places.

    """

    project = Project.objects.get(permalink=permalink)
    if not project:
        return HttpResponseNotFound()

    svg_buffer = io.BytesIO()
    with io.TextIOWrapper(svg_buffer) as output:
        db_resources = Resource.objects.all()
        resources = {resource.name : gantt.Resource(resource.name)
                     for resource in db_resources}

        p = gantt.Project(name='Project 1')

        for resource in db_resources:
            for holiday in resource.holiday_set.all():
                resources[resource.name].add_vacations(holiday.date)

        tasks = Task.arrange_tasks()
        for task in tasks:
            task_obj = gantt.Task(name=task['name'],
                                  start=task['start_date'],
                                  duration=task['duration'],
                                  resources=[resources[task['resource']]])
            p.add_task(task_obj)

        p.make_svg_for_resources(filename=output,
                                 today=tasks[0]['start_date'],
                                 start=tasks[0]['start_date'],
                                 end=(max(task['end_date']
                                          for task in tasks)))

        output.flush()

        return HttpResponse(svg_buffer.getvalue(),
                            content_type="image/svg+xml")



@login_required
def gantt_svg(request):
    return gantt_svg_permalink(request, Project.objects.first().permalink)
