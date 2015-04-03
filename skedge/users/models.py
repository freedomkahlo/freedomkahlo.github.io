from django.db import models

class User(models.Model):
	firstname = models.CharField(max_length=50, default='John')
	lastname = models.CharField(max_length=50, default='Smith')
	password = models.CharField(max_length=20, default='password')
	email = models.EmailField(max_length=75)
	gcalemail = models.EmailField(max_length=75)

	def __str__(self):   
		return self.firstname
