from .models import UserProfile
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	password2 = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'password')

	def clean(self):
		from django.core.validators import validate_email
		from django.core.exceptions import ValidationError

		password1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('password2')
		print password1, password2
		if password1 and password1!= password2:
			raise ValidationError("Passwords don't match")
		email = self.cleaned_data.get('email')
		validate_email(email)
		if User.objects.filter(email=email).exists():
			raise ValidationError("This email is already used")
		return self.cleaned_data



class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ('picture','activation_key')
		exclude = ['activation_key']
