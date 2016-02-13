from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy

from .models import Task, Resource
from .forms import TaskCreateForm, TaskEditForm

def index(request):
    tasks = Task.objects.all()

    context = {'tasks': tasks}
    return render(request, 'schedule/index.html', context)

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

class TaskCreate(CreateView):
    model = Task
    fields = ['name', 'orig_estimate']
    form = TaskCreateForm

    success_url = reverse_lazy('schedule:index')
