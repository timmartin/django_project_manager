from django import forms

from .models import Task

class TaskCreateForm(forms.Form):
    name = forms.CharField()
    orig_estimate = forms.IntegerField()

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'resource', 'estimate_remaining']
