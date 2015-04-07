from django.contrib import admin

from .models import UserProfile, Instance, Invitee

class InviteeInline(admin.TabularInline):
	model = Invitee
class InstanceAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields':['title']}),
		(None,	{'fields':['desc']}), 
		(None, {'fields':['start_date']}),
		(None, {'fields':['end_date']}),
		(None, {'fields':['start_time']}),
		(None, {'fields':['end_time']}),]
	inlines = [InviteeInline]
	list_display = ('title', 'desc', 'pub_date')

admin.site.register(Instance, InstanceAdmin)
admin.site.register(UserProfile)
