import datetime
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task, Resource
from .forms import TaskCreateForm, TaskEditForm

logger = logging.getLogger('project_manager')

@login_required
def index(request):
    tasks = Task.objects.all()

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
    tasks = Task.objects.all()

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
                       'duration': task.current_estimate(),
                       'depends_on': last_tasks[task.resource.name],
                       'resource': task.resource.name})

        resource_available_dates[task.resource.name] = end_date + datetime.timedelta(days=1)

        last_tasks[task.resource.name] = task.name
        
        logger.debug("resource: %s",
                     task.resource.name)
        logger.debug("new date: %s",
                     resource_available_dates[task.resource.name])
    
    return JsonResponse(result, safe=False)
