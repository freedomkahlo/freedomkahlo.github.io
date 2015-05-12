from django.contrib import admin

from .models import UserProfile, Instance, Invitee

class InviteeInline(admin.TabularInline):
	model = Invitee
class InstanceAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields':['title']}),
		(None,	{'fields':['creator']}),
		(None,	{'fields':['desc']}), 
		(None, {'fields':['start_date']}),
		(None, {'fields':['end_date']}),
		(None, {'fields':['start_time']}),
		(None, {'fields':['end_time']}),
		(None, {'fields':['timezone']}),
		(None, {'fields':['event_length']}),
		(None, {'fields':['eventID']}),
		(None, {'fields':['is_scheduled']}),
		(None, {'fields':['scheduled_start']}),
		(None, {'fields':['scheduled_end']}),]
	inlines = [InviteeInline]
	list_display = ('title', 'desc', 'pub_date', 'creator', 'eventID', 'is_scheduled')

admin.site.register(Instance, InstanceAdmin)
admin.site.register(UserProfile)