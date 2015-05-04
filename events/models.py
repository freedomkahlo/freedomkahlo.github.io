from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import pytz

class Instance(models.Model):
	title = models.CharField(max_length=20, default='')
	desc = models.CharField(max_length=100, default='description')
	pub_date = models.DateTimeField('date made')
	start_date = models.CharField(max_length=20, default='')
	end_date = models.CharField(max_length=20, default='')
	start_time = models.CharField(max_length=20, default='')
	end_time = models.CharField(max_length=20, default='')
	event_length = models.CharField(max_length=20, default='')
	creator = models.CharField(max_length=100, default='')
	eventID = models.CharField(max_length=32, default='')
	timezone = models.CharField(max_length=20, default='Eastern')

	is_scheduled = models.BooleanField(default='False')
	scheduled_start = models.DateTimeField('event time', default=datetime.datetime.now())
	scheduled_end = models.DateTimeField('event time', default=datetime.datetime.now())

	def regValidate(self):
		if len(self.title.replace(' ', '')) == 0:
			raise ValidationError('Title cannot be left blank.')
		if self.start_date == '' or self.end_date == '':
			raise ValidationError('Dates cannot be left blank.')
		if self.start_time == '' or self.end_time == '':
			raise ValidationError('Times cannot be left blank.')
		if self.event_length == '':
			raise ValidationError('Event Length cannot be left blank.')
		tz = pytz.timezone('US/' + self.timezone)
		startd = tz.localize(datetime.strptime(self.start_date + ' ' + self.start_time, '%m/%d/%Y %I:%M %p'))
		endd = tz.localize(datetime.strptime(self.end_date + ' ' + self.end_time, '%m/%d/%Y %I:%M %p'))
		if (startd >= endd):
			raise ValidationError('Start time must occur before end time.')
		if (startd.date() < datetime.now(tz).date()):
			raise ValidationError('Start date must occur in the future.')
		self.pub_date = datetime.now(tz)

	def save(self, **kwargs):
		self.regValidate()
		return super(Instance, self).save(**kwargs)

	@property 
	def creatorName(self):
		user = get_object_or_404(User, username=self.creator)
		return user.first_name + ' ' + user.last_name

class PossTime(models.Model):
	event = models.ForeignKey(Instance)
	startTime = models.DateTimeField('start time')
	endTime = models.DateTimeField('end time')
	nFree = models.IntegerField(default = 0)
	peopleList = models.CharField(max_length=100, default='')

	@property
	def date(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return (self.startTime.astimezone(tz)).strftime("%b %d").lstrip("0")
	
	@property
	def time(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return ((self.startTime.astimezone(tz)).strftime("%I:%M %p").lstrip("0")
			+ " - " + (self.endTime.astimezone(tz)).strftime("%I:%M %p %Z").lstrip("0"))

	@property
	def people(self):
		return self.peopleList
	
	def __str__(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return ((self.startTime.astimezone(tz)).strftime("%b %d").lstrip("0") + 
			((self.startTime.astimezone(tz)).strftime("%I:%M %p").lstrip("0")
			+ " - " + (self.endTime.astimezone(tz)).strftime("%I:%M %p %Z").lstrip("0")))

class Invitee(models.Model):
	event = models.ForeignKey(Instance)
	name = models.CharField(max_length=100, default='')
	firstName = models.CharField(max_length=100, default='')
	lastName = models.CharField(max_length=100, default='')
	hasVoted = models.BooleanField(default=False)
	def __str__(self):
		return self.firstName + " " + self.lastName
	def clean(self):
		print (self.name)
		if (len(self.name.replace(' ', '')) == 0):
			raise ValidationError('Name cannot be blank')
		if User.objects.filter(username__iexact=self.name).count() == 0:
			raise ValidationError('%s is not a user.' % self.name)
	def save(self, **kwargs):
		self.clean()
		return super(Invitee, self).save(**kwargs)

#class PotentialTimes(models.Model):
#	event = models.ForeignKey(Instance)
#	time = models.DateTimeField('potential time')
#	votes = models.IntegerField(default = 0)
	
class Message(models.Model):
	event = models.ForeignKey(Instance)
	text = models.CharField(max_length=200, default='')
	author = models.CharField(max_length=100, default='')
	firstName = models.CharField(max_length=100, default='')
	lastName = models.CharField(max_length=100, default='')
	pub_date = models.DateTimeField('date made')
	def __str__(self):
		return text 

class Notification(models.Model):
	user = models.ForeignKey(User)
	notificationType = models.CharField(max_length=50, default='')
	originUserName = models.CharField(max_length=100, default='')
	#event name below, apparently
	desc = models.CharField(max_length=100, default='')
	pub_date = models.DateTimeField('date made')

	def __str__(self):
		if self.notificationType == "deleteNot":
			return self.originUserName + " has deleted '" + self.desc + "'."
		if self.notificationType == "skedgNot":
			return self.originUserName + " has skedguled '" + self.desc + "' and it's in your calendar."

		if self.notificationType == "joinNot":
			return self.originUserName + " has joined '" + self.desc + "'."
		if self.notificationType == "leaveNot":
			return self.originUserName + " has left '" + self.desc + "'."

		if self.notificationType == "composeNot":
			return self.originUserName + " wrote a message in '" + self.desc + "'."
		if self.notificationType == "eraseNot":
			return self.originUserName + " deleted your message in '" + self.desc + "'."

		return self.desc # + " at " + str(self.pub_date)
class UserProfile(models.Model):
	# This line is required. Links UserProfile to a User model instance.
	user = models.OneToOneField(User, related_name="UserProfile")

	# The additional attributes we wish to include.
	refToken = models.CharField(max_length=100, default='')
	picture = models.ImageField(upload_to='profile_images', blank=True)
	activation_key = models.CharField(max_length=40, blank=True)

	# Override the __unicode__() method to return out something meaningful!
	def __unicode__(self):
		return self.user.username

class VetoTime(models.Model):
	event = models.ForeignKey(Instance)
	invitee = models.ForeignKey(Invitee)
	startTime = models.DateTimeField('start time')
	endTime = models.DateTimeField('end time')

	def __str__(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return ((self.startTime.astimezone(tz)).strftime("%I:%M %p").lstrip("0")
			+ " - " + (self.endTime.astimezone(tz)).strftime("%I:%M %p %Z").lstrip("0"))