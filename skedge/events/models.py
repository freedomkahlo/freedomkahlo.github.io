from django.db import models
from django.utils import timezone
class Instance(models.Model):
	title = models.CharField(max_length=20)
	desc = models.CharField(max_length=100, default='description')
	pub_date = models.DateTimeField('date made', default=timezone.now())
	start_date = models.DateField('start date')
	end_date = models.DateField('end date')
	start_time = models.TimeField('start time')
	end_time = models.TimeField('end time')
	def __str__(self):
		return self.title + "\n" + str(self.start_date) + ", " + str(self.start_time) + " to " + str(self.end_date) + ", " + str(self.end_time)
class Invitee(models.Model):
    event = models.ForeignKey(Instance)
    name = models.CharField(max_length=100, default='John Smith')
    def __str__(self):
    	return self.name