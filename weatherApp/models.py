from django.db import models

class Event(models.Model):
  title = models.CharField(max_length = 100)
  description = models.CharField(max_length=250)
  start = models.DateTimeField()
  end = models.DateTimeField()


  def __str__(self):
    return self.title
