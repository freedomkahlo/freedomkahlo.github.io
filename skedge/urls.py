from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    # Examples:
    url(r'^$', views.index, name='index'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^events/', include('events.urls', namespace="events")),
    url(r'^admin/', include(admin.site.urls)),
    ]
