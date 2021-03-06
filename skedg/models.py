from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import pytz

# An Instance is an instance of an event
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

	is_scheduled = models.BooleanField(default=False)
	scheduled_start = models.DateTimeField('event time')
	scheduled_end = models.DateTimeField('event time2')

	@property
	def printScheduledTime(self):
		tz = pytz.timezone('US/' + self.timezone)
		return ((self.scheduled_start.astimezone(tz)).strftime("%b %d") + ", "
			+ (self.scheduled_start.astimezone(tz)).strftime("%I:%M %p").lstrip("0")
			+ " - " + (self.scheduled_end.astimezone(tz)).strftime("%I:%M %p %Z").lstrip("0"))

	@property
	def printDateRange(self):
		date_range = (datetime.strptime(self.start_date, '%m/%d/%Y').strftime("%b %d").replace(' 0', ' ') + ' - ' + 
			datetime.strptime(self.end_date, '%m/%d/%Y').strftime("%b %d").replace(' 0', ' '))
		if date_range.split(' - ')[0] == date_range.split(' - ')[1]:
			return date_range.split(' - ')[0]
		return date_range

	@property
	def printTimeLength(self):
		hours = int(self.event_length.split(':')[0])
		minutes = int(self.event_length.split(':')[1])
		output = ''
		if (hours == 1):
			output = output + "1 hour"
		if (hours > 1):
			output = output + str(hours) + " hours"

		if (minutes > 0):
			if (hours > 0):
				output = output + " "
			output = output + str(minutes) + " minutes"
		return output

	@property
	def printTimeRange(self):
		return self.start_time + ' - ' + self.end_time

	@property
	def hasPassed(self):
		if self.scheduled_end < datetime.now(pytz.utc):
			return True
		else:
			return False

	# Convert the email to a first and last name
	@property
	def creatorName(self):
		user = get_object_or_404(User, username=self.creator)
		return user.first_name + ' ' + user.last_name

# Each instance of PossTime is a possible time that an event can be scheduled for
class PossTime(models.Model):
	event = models.ForeignKey(Instance)
	startTime = models.DateTimeField('start time')
	endTime = models.DateTimeField('end time')
	nFree = models.IntegerField(default = 0)
	peopleList = models.CharField(max_length=1000, default='')

	@property
	def date(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return (self.startTime.astimezone(tz)).strftime("%b") + " " + (self.startTime.astimezone(tz)).strftime("%d").lstrip("0")
	
	@property
	def time(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return ((self.startTime.astimezone(tz)).strftime("%I:%M %p").lstrip("0")
			+ " - " + (self.endTime.astimezone(tz)).strftime("%I:%M %p %Z").lstrip("0"))

	# Convert list of emails who can make it to list of names
	@property
	def people(self):
		split = self.peopleList.split(', ')
		if (split[0] == ''): #No Participants
			return "Everyone has conflicts."
		participants = ''
		for person in split:
			user = get_object_or_404(User, username=person)
			participants += user.first_name + ' ' + user.last_name + ', '
		return participants[0:-2]
	
	def __str__(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return ((self.startTime.astimezone(tz)).strftime("%b %d").lstrip("0") + 
			((self.startTime.astimezone(tz)).strftime("%I:%M %p").lstrip("0")
			+ " - " + (self.endTime.astimezone(tz)).strftime("%I:%M %p %Z").lstrip("0")))

# Model for each user that can make an event
class Invitee(models.Model):
	event = models.ForeignKey(Instance)
	name = models.CharField(max_length=100, default='')
	firstName = models.CharField(max_length=100, default='')
	lastName = models.CharField(max_length=100, default='')
	hasVoted = models.BooleanField(default=False)

	def __str__(self):
		return self.firstName + " " + self.lastName

	# Validate all the fields
	def clean(self):
		print (self.name)
		if (len(self.name.replace(' ', '')) == 0):
			raise ValidationError('Name cannot be blank')
		if User.objects.filter(username__iexact=self.name).count() == 0:
			raise ValidationError('%s is not a user.' % self.name)

	def save(self, **kwargs):
		self.clean()
		return super(Invitee, self).save(**kwargs)

# A message that is posted on the message board
class Message(models.Model):
	event = models.ForeignKey(Instance) # Which event message board
	text = models.CharField(max_length=200, default='')
	author = models.CharField(max_length=100, default='')
	firstName = models.CharField(max_length=100, default='')
	lastName = models.CharField(max_length=100, default='')
	pub_date = models.DateTimeField('date made')
	
	@property 
	def printPubDate(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return (self.pub_date.astimezone(tz)).strftime("%b %d %I:%M %p").replace(' 0', ' ')

	def __str__(self):
		return self.text

# Model for each notification
class Notification(models.Model):
	user = models.ForeignKey(User)
	notificationType = models.CharField(max_length=50, default='')
	originUserName = models.CharField(max_length=100, default='')
	#event name below, apparently
	desc = models.CharField(max_length=100, default='')
	pub_date = models.DateTimeField('date made')

	def __str__(self):
		# Format the text of the notification based on what kind it is
		if User.objects.filter(username__iexact=self.originUserName).count() != 0:
			user = get_object_or_404(User, username=self.originUserName)
			realOriginName = user.first_name + ' ' + user.last_name
		else: 
			realOriginName = self.originUserName

		if self.notificationType == "deleteNot":
			return realOriginName + " has deleted '" + self.desc + "'."
		if self.notificationType == "noTimeNot":
			return "'" + self.desc + "'" + " has expired."
		if self.notificationType == "skedgNot":
			return realOriginName + " has scheduled '" + self.desc + "' and it's in your Google Calendar."

		if self.notificationType == "joinNot":
			return realOriginName + " has joined '" + self.desc + "'."
		if self.notificationType == "leaveNot":
			return realOriginName + " has left '" + self.desc + "'."

		if self.notificationType == "composeNot":
			return realOriginName + " wrote a message in '" + self.desc + "'."
		if self.notificationType == "eraseNot":
			return realOriginName + " deleted your message in '" + self.desc + "'."

		if self.notificationType == "bootNot":
			return realOriginName + " has booted you from '" + self.desc + "'."

		return self.desc

# A User profile associated with each user, giving additional user information
class UserProfile(models.Model):
	# This line is required. Links UserProfile to a User model instance.
	user = models.OneToOneField(User, related_name="UserProfile")

	# The additional attributes we wish to include.
	refToken = models.CharField(max_length=100, default='')
	activation_key = models.CharField(max_length=40, blank=True)
	activated = models.BooleanField(default=False)
	firstTimeHome = models.BooleanField(default=True)
	firstTimeEventAsCreator = models.BooleanField(default=True)
	firstTimeEventAsInvitee = models.BooleanField(default=True)
	login_key = models.CharField(max_length=40, blank=True)

	def __unicode__(self):
		return self.user.username

# Each time that each user adds a conflict, one of these is created
class VetoTime(models.Model):
	event = models.ForeignKey(Instance)
	invitee = models.ForeignKey(Invitee)
	startTime = models.DateTimeField('start time')
	endTime = models.DateTimeField('end time')

	def __str__(self):
		tz = pytz.timezone('US/' + self.event.timezone)
		return ((self.startTime.astimezone(tz)).strftime("%I:%M %p").lstrip("0")
			+ " - " + (self.endTime.astimezone(tz)).strftime("%I:%M %p %Z").lstrip("0"))