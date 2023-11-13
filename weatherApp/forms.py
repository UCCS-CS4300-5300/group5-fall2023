from django import forms
#from django.forms import ModelForm
from .models import Event
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#This class allows for more specific customization of each field in the database
class EventForm(forms.Form):
  #Title field
  title = forms.CharField(
    label = "Title",
    required = True,
    max_length = 100,
    widget = forms.TextInput(
      attrs = {'class': 'form-control'}
    ),
  )

  #Description Field
  description = forms.CharField(
    label = "Description",
    required = True,
    widget = forms.TextInput({'class': 'form-control',}),
  )

  #DateTimeStart
  start = forms.DateTimeField(
    label = "Start Date and Time",
    required = True,
    widget = forms.DateInput({
      'class': 'form-control',
      'type': 'datetime-local',
    })
  )

  end = forms.DateTimeField(
    label = "End Date and Time",
    required = True,
    widget = forms.DateInput({
      'class': 'form-control',
      'type': 'datetime-local',
    })
  )
  

class CustomUserCreationForm(UserCreationForm):
  first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
  last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
  email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

  class Meta:
      model = User
      fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )