from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.views import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ChangeLocationForm, EventForm, UserSettingForm, CustomUserCreationForm
from .models import Event, UserSetting, Location, Weather
from .serializers import EventModelSerializer
from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
import requests
from datetime import datetime
from rest_framework import viewsets


def index(request):
  weather_data = "Log In, Sign Up, or Change Location"
  location = "No Location"
  hazardous = []
  if request.user.is_anonymous:
    event_list = list(Event.objects.all().order_by('start').filter(user=1))[:5]
  else:
    event_list = list(
        Event.objects.all().order_by('start').filter(user=request.user))[:5]
    location = Location.objects.all().order_by('state').filter(
        user=request.user).first()
    if location:
      weather_data = get_weather(
          request.user)['properties']['periods'][0]['detailedForecast']
      hazardous = get_hazardous_events(request.user,
                                       get_weather(request.user)['properties'])

  return render(
      request, 'weatherApp/index.html', {
          'event_list': event_list,
          'weather_data': weather_data,
          'location': location,
          'hazardous': hazardous
      })


def allEvents(request):
  event_list = list(
      Event.objects.all().order_by('start').filter(user=request.user))

  return render(request, 'weatherApp/allEvents.html',
                {'event_list': event_list})


def eventDetails(request, id):

  weather = "No Forecast Data"
  icon = ""

  if request.user.is_anonymous:
    event = Event.objects.get(pk=id)
  else:
    event = Event.objects.get(pk=id)
    location = Location.objects.all().order_by('state').filter(
        user=request.user).first()
    if location:
      weather_data = get_weather(request.user)['properties']['periods']

      # Goes through the API response and adds icons when able
      for period in weather_data:

        period_time = timeParse(period['startTime'])

        period_end = timeParse(period['endTime'])

        # checking to see if period lands in range of any events
        if period_time < period_end:
          in_range = event.start >= period_time and event.start <= period_end
        else:  # crosses midnight
          in_range = event.start >= period_time or event.start <= period_end

        if in_range:
          weather = period['detailedForecast']
          icon = period['icon']

  return render(request, 'weatherApp/eventDetails.html', {
      "event": event,
      "weather": weather,
      "icon": icon
  })


def headerBar(request):
  return render(request, 'weatherApp/includes/headerBar.html')


# Function to make getting a datetime from api time easier
def timeParse(period_time):
  period_time = period_time.split('T')
  day = period_time[0]
  time = period_time[1].split('-')
  offset = time[1].split(':')
  period_time = day + time[0] + '-' + offset[0] + offset[1]
  return datetime.strptime(period_time, '%Y-%m-%d%X%z')


# This takes the weather and a user's events, and returns a list of hazardous events
def get_hazardous_events(this_user, weather):
  event_list = list(
      Event.objects.all().order_by('start').filter(user=this_user))
  if UserSetting.objects.filter(user=this_user).exists():
    weather_preference = list(
        UserSetting.objects.all().filter(user=this_user))[0]
    weather_preference = weather_preference.weather_notifs
  else:
    weather_preference = "Disabled"
  hazardous_events = []

  # Checking each period
  for period in weather['periods']:

    period_time = timeParse(period['startTime'])

    period_end = timeParse(period['endTime'])

    # Checking if any events are in this period
    for event in event_list:

      # checking to see if period lands in range of any events
      if period_time < period_end:
        in_range = event.start >= period_time and event.start <= period_end
      else:  # crosses midnight
        in_range = event.start >= period_time or event.start <= period_end

      # if events are in range and the weather is bad, add to the hazardous list

      if in_range:

        # If enabled, so default, reasonable weather preferences
        if weather_preference == "Enabled":
          wind_pref = 15
          temperature_pref = 50
          precip_pref = 0

        # Enabled, but only extreme conditions, so amplifies
        elif weather_preference == "Extreme conditions only":
          wind_pref = 30
          temperature_pref = 32
          precip_pref = 50

        # Disabled, make it so the hazards never trigger
        else:
          wind_pref = 1500
          temperature_pref = -5000
          precip_pref = 200

        # Getting wind speed
        wind = period['windSpeed'].split(" ")
        if len(wind) == 2:
          wind = int(wind[0])
        else:
          wind = int(wind[2])

        # Getting precip chance
        precip = period['probabilityOfPrecipitation']['value']
        if precip == None:
          precip = 0
        else:
          precip = int(precip)

        # Getting temperature
        temperature = int(period['temperature'])

        #if wind > wind_pref or temperature > temperature_pref or precipitation != 0:
        if wind > wind_pref or temperature < temperature_pref or precip > precip_pref:
          hazardous_events.append({"event": event, "icon": period['icon']})

  return hazardous_events


#This is the Create Event Page
@csrf_exempt  #did not want to work
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
      event = Event.objects.create(title=title_event,
                                   description=description_event,
                                   start=start_event,
                                   end=end_event,
                                   user=request.user)
      event.save()
      return HttpResponseRedirect('/')
  else:
    form = EventForm()

  return render(request, 'weatherApp/addEvent.html', {'event_form': form})


#View for adjusting user settings
@csrf_exempt
def editUserSetting(request):
  user_profile = request.user
  if request.method == 'POST':
    form = UserSettingForm(request.POST)
    if form.is_valid():
      notif_preference = form.cleaned_data['weather_notifs']
      # check if object already exists for this user so it can just
      # be updated, otherwise create a new one for them
      if UserSetting.objects.filter(user=user_profile).exists():
        user_setting = UserSetting.objects.get(user=user_profile)
        user_setting.weather_notifs = notif_preference
        user_setting.save()
      else:
        user_setting = UserSetting.objects.create(
            user=user_profile, weather_notifs=notif_preference)
        user_setting.save()

  else:
    initial_data = {'weather_notifs': "Disabled"}
    if UserSetting.objects.filter(user=user_profile).exists():
      user_setting = UserSetting.objects.get(user=user_profile)
      initial_data['weather_notifs'] = user_setting.weather_notifs
    form = UserSettingForm(initial=initial_data)

  return render(request, 'weatherApp/weatherNotifications.html',
                {'user_settings_form': form})


def get_location_from_ip(ip_address):
  response = requests.get("http://ip-api.com/json/{}".format(ip_address))
  return response.json()


#update the specific item in the database
@csrf_exempt
def updateEvent(request, id):
  event = Event.objects.get(id=id)

  if request.method == 'POST':
    form = EventForm(request.POST or None)
    if form.is_valid():
      #Update the specific field
      event.title = form.cleaned_data['title']
      event.description = form.cleaned_data['description']
      event.start = form.cleaned_data['start']
      event.end = form.cleaned_data['end']

      event.save()
      return HttpResponseRedirect("/")

  else:
    #Fill in data to the page. NOTE: Does not fill in DateTimeField Currently
    form = EventForm(
        initial={
            'title': event.title,
            'description': event.description,
            'start': event.start,
            'end': event.end,
        })

  return render(request, "weatherApp/updateEvent.html", {'event_form': form})


#delete and return to front page
def deleteEvent(request, id):
  #Try and see if it is able to. If not redirect to home anyways.
  try:
    event = Event.objects.get(id=id)
    event.delete()
    return HttpResponseRedirect("/")
  except Event.DoesNotExist:
    return HttpResponseRedirect("/")


#def get_location_from_ip(ip_address):
#  response = requests.get("http://ip-api.com/json/{}".format(ip_address))
#  return response.json()


def get_weather(user):  #_from_ip(request):
  #  ip_address = request.GET.get("ip")
  #  location = get_location_from_ip(ip_address)
  #  city = location.get("city")
  #  country_code = location.get("countryCode")

  # getting location from user:
  user_location = Location.objects.get(user=user)
  address = user_location.city + "," + user_location.state
  weather_data = get_location(address)  #(city, country_code)
  return (weather_data)


#  description = weather_data['weather'][0]['description']
#  temperature = weather_data['main']['temp']
#  s = "You're in {}, {}. You can expect {} with a temperature of {} F.".format(city, country_code, description, temperature)
#  data = {"weather_data": s}
#  return JsonResponse(data)


def get_location(address):  #(city, country_code):
  address_url = " https://geocode.maps.co/search?q={address}".format(
      address=address)
  address_response = requests.get(address_url)
  address_json = address_response.json()
  lat = address_json[0]['lat']
  lon = address_json[0]['lon']
  url_url = "https://api.weather.gov/points/{latitude},{longitude}".format(
      latitude=lat, longitude=lon)
  #"http://api.openweathermap.org/data/2.5/weather?q={},{}&appid=a8e71c9932b20c4ceb0aed183e6a83bb&units=imperial".format(city, country_code)
  url_response = requests.get(url_url)
  url_json = url_response.json()
  url = url_json['properties']['forecast']
  response = requests.get(url)
  return response.json()


class SignUpView(generic.CreateView):
  form_class = CustomUserCreationForm
  success_url = reverse_lazy('login')
  template_name = 'weatherApp/signup.html'


class LoginView(AuthLoginView):
  template_name = 'weatherApp/login.html'


def settings(request):
  return render(request, 'weatherApp/settings_page.html')


class EventModelViewSet(viewsets.ModelViewSet):
  queryset = Event.objects.all()
  serializer_class = EventModelSerializer


@csrf_exempt
def changeLocation(request):
  user_profile = request.user
  if request.method == 'POST':
    form = ChangeLocationForm(request.POST)
    if form.is_valid():
      city_pref = form.cleaned_data['city']
      state_pref = form.cleaned_data['state']
      # check if the user already has a location object
      if Location.objects.filter(user=user_profile).exists():
        location_pref = Location.objects.get(user=user_profile)
        location_pref.city = city_pref
        location_pref.state = state_pref
        location_pref.save()
      else:
        location_pref = Location.objects.create(city=city_pref,
                                                state=state_pref,
                                                user=user_profile)
        location_pref.save()

  else:
    initial_data = {'city': "", 'state': ""}
    if Location.objects.filter(user=user_profile).exists():
      location_pref = Location.objects.get(user=user_profile)
      initial_data['city'] = location_pref.city
      initial_data['state'] = location_pref.state
    form = ChangeLocationForm(initial=initial_data)

  return render(request, 'weatherApp/changeLocation.html', {'form': form})
