from django import forms

class TaskCreateForm(forms.Form):
    name = forms.CharField()
    orig_estimate = forms.IntegerField()
