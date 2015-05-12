from .models import UserProfile
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	password2 = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'password')

	# Validate that the user form information is valid
	def clean(self):
		from django.core.validators import validate_email
		from django.core.exceptions import ValidationError

		password1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('password2')
		if password1 and password1!= password2:
			raise ValidationError("Passwords don't match")
		email = self.cleaned_data.get('username')
		validate_email(email)
		if User.objects.filter(username=email.lower()).exists():
			raise ValidationError("This email is already used")
		if (not self.cleaned_data.get('first_name')) or (not self.cleaned_data.get('last_name')):
			raise ValidationError("Please enter your name")
		return self.cleaned_data