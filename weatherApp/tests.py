from django.test import TestCase, Client
from .models import Event, UserSetting
from .views import index, allEvents, editUserSetting
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import CustomUserCreationForm, EventForm
from rest_framework import status


# Test Cases for views.py
class EventCRUDTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(username='testuser',
                                         password='testpassword')
    self.client.login(username='testuser', password='testpassword')

    Event.objects.create(title="Test Event",
      description="Test Description",
      start=datetime(2023, 11, 8, 10, 15, 0),
      end=datetime(2023, 11, 8, 12, 30, 0),
      user=self.user)

  def test_create_view(self): 

    response = self.client.get(reverse('createEvent'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "weatherApp/addEvent.html")
  
  def test_create_event(self):

    response = self.client.post(reverse('createEvent'), 
                                {'title' : "Test Event",
                                 'description' : "Test Description",
                                 'start' : datetime(2023, 11, 8, 10, 15, 0),
                                 'end' : datetime(2023, 11, 8, 12, 30, 0)})
    self.assertEqual(response.status_code, 302)

  def test_update_view(self):

    response = self.client.get(reverse('updateEvent', args =[1]))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "weatherApp/updateEvent.html")
  
  def test_update_event(self):

    newData = {
      'title' : 'New Title',
      'description' : 'New Description',
      'start' : timezone.make_aware(datetime(2023, 11, 7, 10, 15, 0)),
      'end' : timezone.make_aware(datetime(2023, 11, 7, 12, 30, 0)),
    }

    response = self.client.post(reverse('updateEvent', args = [1]), data=newData)
    self.assertEqual(response.status_code, 302)

  def test_delete_event(self):
    response = self.client.post(reverse('deleteEvent', args = [1]))
    self.assertEqual(response.status_code, 302)



