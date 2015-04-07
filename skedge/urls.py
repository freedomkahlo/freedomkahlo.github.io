from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    # Examples:
    url(r'^events/', include('events.urls', namespace="events")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('events.urls', namespace='events')),
    ]
