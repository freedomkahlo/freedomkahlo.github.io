from django.contrib import admin

from .models import Desc, Invitee, InitTime

class InviteeInline(admin.TabularInline):
	model = Invitee
class InitTimeInline(admin.StackedInline):
	model = InitTime
	extra = 1
class DescAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields':['title']}),
		(None,	{'fields':['desc']})]
	inlines = [InviteeInline, InitTimeInline]
	list_display = ('title', 'desc', 'pub_date')

admin.site.register(Desc, DescAdmin)
