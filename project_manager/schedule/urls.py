from django.conf.urls import url

from . import views

app_name = 'schedule'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tasks/(?P<pk>[0-9]+)/edit/$',
        views.TaskEdit.as_view(),
        name='edit_task'),
    url(r'^resource-weekly/(?P<resource_id>[a-zA-Z0-9]+)',
        views.resource_weekly_usage),
    url(r'^tasks/add/$',
        views.TaskCreate.as_view(),
        name='add_task'),
    url(r'^gantt-json$', views.gantt_json),
    url(r'^gantt-svg$', views.gantt_svg, name="gantt_svg"),
    url(r'^gantt-svg/p/(?P<permalink>[a-zA-Z0-9]+)',
        views.gantt_svg_permalink,
        name="gantt_svg_permalink")
]
