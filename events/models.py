from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import *
from django.contrib.auth.models import User

class Instance(models.Model):
	title = models.CharField(max_length=20, default='')
	desc = models.CharField(max_length=100, default='description')
	pub_date = models.DateTimeField('date made')
	start_date = models.DateField('start date')
	end_date = models.DateField('end date')
	start_time = models.TimeField('start time')
	end_time = models.TimeField('end time')
	def clean(self):
		if len(self.title.replace(' ', '')) == 0:
			raise ValidationError('Title cannot be left blank.')
		if self.start_date == '' or self.end_date == '':
			raise ValidationError('Dates cannot be left blank.')
		if self.start_time == '' or self.end_time == '':
			raise ValidationError('Times cannot be left blank.')
		startd = datetime.strptime(self.start_date + ' ' + self.start_time, '%Y-%m-%d %H:%M')
		endd = datetime.strptime(self.end_date + ' ' + self.end_time, '%Y-%m-%d %H:%M')
		if (startd >= endd):
			raise ValidationError('Start time must occur before end time.')
		if (startd < datetime.now() - timedelta(0, 60)):
			raise ValidationError('Start date must occur in the future.')
		self.pub_date = timezone.now()
	def __str__(self):
		return self.title + "\n" + self.start_date + ", " + self.start_time + " to " + self.end_date + ", " + self.end_time
	def save(self, **kwargs):
		self.clean()
		return super(Instance, self).save(**kwargs)

class Invitee(models.Model):
	event = models.ForeignKey(Instance)
	name = models.CharField(max_length=100)
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