from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import EventForm
from .models import Event


def index(request):
  event_list = list(Event.objects.all().order_by('start'))[:5]
  return render(request, 'weatherApp/index.html', {'event_list': event_list})

def allEvents(request):
  event_list = list(Event.objects.all().order_by('start'))
  return render(request, 'weatherApp/allEvents.html', {'event_list': event_list})



#This is the Create Event Page
@csrf_exempt #did not want to work
def createEvent(request):
  #checks that during a Post request that the inputs are valid
  if request.method == 'POST':
    form = EventForm(request.POST)
    if form.is_valid():

      #taking the values from the form page
      title_event = form.cleaned_data['title']
      description_event = form.cleaned_data['description']
      start_event = form.cleaned_data['start']
      end_event = form.cleaned_data['end']

      #Storing them into the database
      event = Event.objects.create(
        title = title_event,
        description = description_event,
        start = start_event,
        end = end_event,
      )
      event.save()
      return HttpResponse('New Event Added!') 
      
  else:
    form = EventForm()
      
  return render(request, 'weatherApp/addEvent.html', {'event_form': form})
      