from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import *
from django.contrib.auth.models import User

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

	is_scheduled = models.BooleanField(default='False')

	def regValidate(self):
		if len(self.title.replace(' ', '')) == 0:
			raise ValidationError('Title cannot be left blank.')
		if self.start_date == '' or self.end_date == '':
			raise ValidationError('Dates cannot be left blank.')
		if self.start_time == '' or self.end_time == '':
			raise ValidationError('Times cannot be left blank.')
		if self.event_length == '':
			raise ValidationError('Event Length cannot be left blank.')
		startd = datetime.strptime(self.start_date + ' ' + self.start_time, '%m/%d/%Y %I:%M %p')
		endd = datetime.strptime(self.end_date + ' ' + self.end_time, '%m/%d/%Y %I:%M %p')
		if (startd >= endd):
			raise ValidationError('Start time must occur before end time.')
		# timedelta(hours=4) is a temporary fix. Forces EST.
		if (startd < datetime.now() - timedelta(minutes=1) - timedelta(hours=4)):
			raise ValidationError('Start date must occur in the future.')
		self.pub_date = timezone.now()

	def save(self, **kwargs):
		self.regValidate()
		return super(Instance, self).save(**kwargs)

class PossTime(models.Model):
	event = models.ForeignKey(Instance)
	startTime = models.DateTimeField('start time')
	endTime = models.DateTimeField('end time')
	nConflicts = models.IntegerField(default = 0)

	def __str__(self):
		# This is temporary timezone
		startPrint = self.startTime - timedelta(hours=4)
		endPrint = self.endTime - timedelta(hours=4)
		return startPrint.strftime("%b %d %I:%M %p") + " - " + endPrint.strftime("%I:%M %p")

	@property
	def strCreator(self):
		# This is temporary timezone
		startPrint = self.startTime - timedelta(hours=4)
		endPrint = self.endTime - timedelta(hours=4)
		return startPrint.strftime("%b %d %I:%M %p") + " - " + endPrint.strftime("%I:%M %p") + "-- Conflicts: " + str(self.nConflicts)

class Invitee(models.Model):
	event = models.ForeignKey(Instance)
	name = models.CharField(max_length=100)
	hasVoted = models.BooleanField(default=False)
	def __str__(self):
		return self.name
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
	
class Notification(models.Model):
	user = models.ForeignKey(User)
	desc = models.CharField(max_length=100)
	pub_date = models.DateTimeField('date made')

	def __str__(self):
		return self.desc + " at " + str(self.pub_date)
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