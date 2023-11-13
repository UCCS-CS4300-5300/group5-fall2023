from django.db import models
from django.conf import settings

class Event(models.Model):
  title = models.CharField(max_length = 100)
  description = models.CharField(max_length=250)
  start = models.DateTimeField()
  end = models.DateTimeField()
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


  def __str__(self):
    return self.title
