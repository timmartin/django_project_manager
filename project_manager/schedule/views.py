import datetime
import logging
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task, Resource
from .forms import TaskCreateForm, TaskEditForm

import gantt

logger = logging.getLogger('project_manager')

@login_required
def index(request):
    tasks = Task.objects.all().order_by('pk')

    context = {'tasks': tasks}
    return render(request, 'schedule/index.html', context)

@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task.name = request.POST['name']
        task.days_worked = request.POST['days_worked']
        task.estimate_remaining = request.POST['estimate_remaining']
        task.resource = Resource.objects.get(pk=request.POST['resource'])
        task.save()
        return redirect('schedule:index')    

    form = TaskEditForm(instance=task)
    
    context = {'task': task, 'form': form}
    return render(request, 'schedule/edit_task.html', context)


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['name', 'orig_estimate', 'resource', 'project']
    form = TaskCreateForm

    success_url = reverse_lazy('schedule:index')


@login_required
def gantt_json(request):
    return JsonResponse(Task.arrange_tasks(), safe=False)

@login_required
def gantt_svg(request):
    
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
