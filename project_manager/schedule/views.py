from django.shortcuts import render, redirect, get_object_or_404

from .models import Task

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
        task.save()
        return redirect('schedule:index')    
    
    context = {'task': task}
    return render(request, 'schedule/edit_task.html', context)
