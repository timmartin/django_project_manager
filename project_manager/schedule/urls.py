from django.conf.urls import url

from . import views

app_name = 'schedule'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tasks/(?P<pk>[0-9]+)/edit/$', views.edit_task, name='edit_task'),
    url(r'^tasks/add/$', views.TaskCreate.as_view(), name='add_task'),
    url(r'^gantt-json$', views.gantt_json),
    url(r'^gantt-svg$', views.gantt_svg, name="gantt_svg")
]
