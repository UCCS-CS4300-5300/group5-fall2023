from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path("createEvent", views.createEvent, name="createEvent"),
  path("allEvents", views.allEvents, name="allEvents")
]