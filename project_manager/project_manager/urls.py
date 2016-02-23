from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^schedule/', include('schedule.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
]
