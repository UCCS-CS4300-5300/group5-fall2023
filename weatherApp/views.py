from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse

from .forms import EventForm


def index(request):
  return render(request, 'weatherApp/index.html')


def createEvent(request):
  if request.method == 'POST':
    event = EventForm(request.POST)
  
    if event.is_valid():
      event.save()
      return HttpResponse('New Event Added!')
  else:
    event = EventForm()
      
  return render(request, 'weatherApp/addEvent.html', {'createEvent': event})

      