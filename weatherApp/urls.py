from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path('get_weather_from_ip/', views.get_weather_from_ip, name="get_weather_from_ip"),
]