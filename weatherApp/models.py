from django.db import models
from django.conf import settings


class Event(models.Model):
  title = models.CharField(max_length=100)
  description = models.CharField(max_length=250)
  start = models.DateTimeField()
  end = models.DateTimeField()
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

  def __str__(self):
    return self.title

class UserSetting(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  weather_notifs = models.CharField(max_length=100)

  def __str__(self):
    return self.user.username


class Location(models.Model):
  #address = models.CharField(max_length = 200)
  city = models.CharField(max_length=100)
  state = models.CharField(max_length=100)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

  def __str__(self):
    return self.city + ", " + self.state


class Weather(models.Model):
  description = models.CharField(max_length=250)
  temperature = models.IntegerField()
  wind_speed = models.CharField(max_length=50)
