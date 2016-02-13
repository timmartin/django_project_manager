from django.conf.urls import url

from . import views

app_name = 'schedule'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^task/(?P<pk>[0-9]+)/edit/$', views.edit_task, name='edit_task')
]
