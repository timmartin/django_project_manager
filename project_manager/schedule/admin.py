from django.contrib import admin

from .models import Task, Resource

admin.site.register(Task)
admin.site.register(Resource)
