from django.contrib import admin

from .models import Project, Task, Resource, ResourceUsage, Holiday

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Resource)
admin.site.register(ResourceUsage)
admin.site.register(Holiday)
