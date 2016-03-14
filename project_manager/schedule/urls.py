from django.conf.urls import url

from . import views

app_name = 'schedule'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tasks/(?P<pk>[0-9]+)/edit/$',
        views.TaskEdit.as_view(),
        name='edit_task'),

    # View and update the mapping of resources to tasks on a daily
    # basis
    url(r'^resource-weekly/view/(?P<resource_id>[a-zA-Z0-9]+)',
        views.resource_weekly_usage),
    url(r'^resource-weekly/update',
        views.resource_usage_update,
        name="update_resource_usage"),
    
    url(r'^tasks/add/$',
        views.TaskCreate.as_view(),
        name='add_task'),

    # JSON API for Gantt chart data
    url(r'^gantt-json$', views.gantt_json),

    # The Gantt chart as SVG XML
    url(r'^gantt-svg$', views.gantt_svg, name="gantt_svg"),
    url(r'^gantt-svg/p/(?P<permalink>[a-zA-Z0-9]+)',
        views.gantt_svg_permalink,
        name="gantt_svg_permalink")
]
