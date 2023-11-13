from django.test import TestCase, Client
from .models import Event
from .views import index, allEvents
from datetime import datetime
from django.urls import reverse

# Test Cases for views.py
class EventViewTestCase(TestCase):
  # Create a test event for testing whether it gets added to the views
  def setUp(self):
    Event.objects.create(
      title = "Test Event",
      description = "Test Description",
      start = datetime(2023, 11, 8, 10, 15, 0),
      end = datetime(2023, 11, 8, 12, 30, 0)
    )
  def test_index_view(self):
    # reverse index view and assert that it gets back 200 responce
    response = self.client.get(reverse('index'))
    self.assertEqual(response.status_code, 200)
    # assert that the page contains new event
    self.assertContains(response, '<li class="w3-hover-light-grey">Test Event - Nov. 8, 2023, 10:15 a.m. to Nov. 8, 2023, 12:30 p.m.</li>')
    self.assertQuerysetEqual(
      response.context['event_list'],
      ['<Event: Test Event>'],
      ordered=False
    )
  def test_allEvents_view(self):
    # similar to previous test, but for allEvents view
    response = self.client.get(reverse('allEvents'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '<li class="w3-hover-light-grey">Test Event - Nov. 8, 2023, 10:15 a.m. to Nov. 8, 2023, 12:30 p.m.</li>')
    self.assertQuerysetEqual(
      response.context['event_list'],
      ['<Event: Test Event>'],
      ordered=False
    )