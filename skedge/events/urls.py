from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^(?P<instance_id>[0-9]+)/$', views.detail, name='detail'),
	url(r'^add/', views.add, name='add'),
    url(r'^$', views.index, name='index'),
]