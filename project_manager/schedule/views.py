import datetime
import logging
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Project, Task, Resource
from .forms import TaskCreateForm, TaskEditForm

import gantt

logger = logging.getLogger('project_manager')

@login_required
def index(request):
    tasks = Task.objects.filter(estimate_remaining__gt=0).order_by('pk')
    completed_tasks = Task.objects.filter(estimate_remaining=0).order_by('pk')

    context = {'tasks': tasks,
               'completed_tasks': completed_tasks,
               'project': Project.objects.first()}
    return render(request, 'schedule/index.html', context)


def resource_weekly_usage(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)

    context = {'resource': resource,
               'tasks': Task.objects.all()}
    
    return render(request, 'schedule/resource_weekly_usage.html', context)


class TaskEdit(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['name', 'resource', 'days_worked', 'estimate_remaining']
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
        resources = {resource.name : gantt.Resource(resource.name)
                     for resource in Resource.objects.all()}

        p = gantt.Project(name='Project 1')

        tasks = Task.arrange_tasks()
        for task in tasks:
            task_obj = gantt.Task(name=task['name'],
                                  start=task['start_date'],
                                  duration=task['duration'],
                                  resources=[resources[task['resource']]])
            p.add_task(task_obj)

        p.make_svg_for_tasks(filename=output,
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
