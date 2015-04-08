from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^(?P<instance_id>[0-9]+)/$', views.detail, name='detail'),
	url(r'^add/', views.add, name='add'),
	url(r'^delete/', views.delete, name='delete'),
	url(r'^deleteInvitee/', views.deleteInvitee, name='deleteInvitee'),
	url(r'^register/$', views.register, name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^$', views.index, name='index'),
]