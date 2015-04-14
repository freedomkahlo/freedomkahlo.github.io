from django.db import models
from django.core.exceptions import ValidationError
from datetime import *
from django.contrib.auth.models import User

class Instance(models.Model):
	title = models.CharField(max_length=20, default='')
	desc = models.CharField(max_length=100, default='description')
	pub_date = models.DateTimeField('date made')
	start_date = models.CharField(max_length=20)
	end_date = models.CharField(max_length=20)
	start_time = models.TimeField('start time')
	end_time = models.TimeField('end time')
	creator = models.CharField(max_length=100, default='')

	is_scheduled = models.BooleanField(default='False')

	def regValidate(self):
		if len(self.title.replace(' ', '')) == 0:
			raise ValidationError('Title cannot be left blank.')
		if self.start_date == '' or self.end_date == '':
			raise ValidationError('Dates cannot be left blank.')
		if self.start_time == '' or self.end_time == '':
			raise ValidationError('Times cannot be left blank.')
		startd = datetime.strptime(self.start_date + ' ' + self.start_time, '%m/%d/%Y %H:%M %p')
		endd = datetime.strptime(self.end_date + ' ' + self.end_time, '%m/%d/%Y %H:%M %p')
		if (startd >= endd):
			raise ValidationError('Start time must occur before end time.')
		if (startd < datetime.now() - timedelta(0, 60)):
			raise ValidationError('Start date must occur in the future.')
		self.pub_date = datetime.now()

	def adminValidate(self):
		if len(self.title.replace(' ', '')) == 0:
			raise ValidationError('Title cannot be left blank.')
		startd = datetime.combine(self.start_date, self.start_time)
		endd = datetime.combine(self.start_date, self.start_time)
		if (startd >= endd):
			raise ValidationError('Start time must occur before end time.')
		if (startd < datetime.now() - timedelta(0, 60)):
			raise ValidationError('Start date must occur in the future.')
		self.pub_date = datetime.now()

	
		return self.title + "\n" + str(self.start_date) + ", " + str(self.start_time) + " to " + str(self.end_date) + ", " + str(self.end_time)
	def save(self, **kwargs):
		if (type(self.start_date) == datetime):
			self.adminValidate()
		else:
			self.regValidate()
		return super(Instance, self).save(**kwargs)

class PossTime(models.Model):
	event = models.ForeignKey(Instance)
	startTime = models.DateTimeField('start time', default=datetime.now())
	endTime = models.DateTimeField('end time', default=datetime.now())
	nConflicts = models.IntegerField(default = 0)

	def __str__(self):
		self.startTime.strftime("%Y/%m/%d %H:%M:%S")

class Invitee(models.Model):
	event = models.ForeignKey(Instance)
	userID = models.IntegerField(default='0')
	name = models.CharField(max_length=100)
	rsvpAccepted = models.BooleanField(default=None)
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

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username