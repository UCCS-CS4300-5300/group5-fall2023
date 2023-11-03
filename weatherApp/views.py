from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse
from django.http import JsonResponse
import requests

def index(request):
  return render(request, 'weatherApp/index.html')

def get_location_from_ip(ip_address):
  response = requests.get("http://ip-api.com/json/{}".format(ip_address))
  return response.json()

def get_weather_from_ip(request):
  ip_address = request.GET.get("ip")
  location = get_location_from_ip(ip_address)
  city = location.get("city")
  country_code = location.get("countryCode")
  weather_data = get_weather_from_location(city, country_code)
  description = weather_data['weather'][0]['description']
  temperature = weather_data['main']['temp']
  s = "You're in {}, {}. You can expect {} with a temperature of {} degrees.".format(city, country_code, description, temperature)
  data = {"weather_data": s}
  return JsonResponse(data)

def get_weather_from_location(city, country_code):
  url = "http://api.openweathermap.org/data/2.5/weather?q={},{}&appid=a8e71c9932b20c4ceb0aed183e6a83bb&units=metric".format(city, country_code)
  response = requests.get(url)
  return response.json()

