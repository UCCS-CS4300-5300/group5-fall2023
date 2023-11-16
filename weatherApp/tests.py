from django.test import TestCase, Client
from .models import Event
from .views import index, allEvents
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm

# Test Cases for views.py
class EventCRUDTestCase(TestCase):
  def setup(self):
    Event.objects.create(
      title = "Test Event",
      description = "Test Description",
      start = datetime(2023, 11, 8, 10, 15, 0),
      end = datetime(2023, 11, 8, 12, 30, 0)
    )
    
  def test_create_event(self):
    #Unit Test
    createEvent = Event.objects.get(title="Test Event")
    self.assertEqual(str(createEvent), "Test Event")

    #Integration Test
    response = self.client.get(reverse('createEvent'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "addEvent.html")

  def test_update_event(self):
    updateEvent = Event.objects.get(title="Test Event")

    newData = {
      'title' : 'New Title',
      'description' : 'New Description',
    }

    response = self.client.post('updateEvent', data=newData)
    self.assertEqual(response.status_code, 302)
    self.assertEqual(str(response), "New Title")

  #Needs to be fixed
  #def test_delete_event(self):
    #deleteEvent = Event.objects.get(title="Test Event")
    #response = self.client.post('deleteEvent', deleteEvent)
    #self.assertEqual(response, )





class EventViewTestCase(TestCase):
  # Create a test event for testing whether it gets added to the views
  def setUp(self):
    event = Event.objects.create(
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

class CustomUserCreationFormTest(TestCase):

  def test_form_validity(self):
    form_data = {
        'username': 'newuser',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@example.com',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    }
    form = CustomUserCreationForm(data=form_data)
    self.assertTrue(form.is_valid())

  def test_form_invalidity(self):
    form_data = {
        'username': 'newuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    }
    form = CustomUserCreationForm(data=form_data)
    self.assertFalse(form.is_valid()) 

class SignupViewTest(TestCase):

  def test_signup_page_status_code(self):
    response = self.client.get(reverse('signup'))
    self.assertEqual(response.status_code, 200)

  def test_signup_form(self):
    response = self.client.post(reverse('signup'), data={
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser@example.com',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    })
    self.assertEqual(User.objects.count(), 1)

class LoginViewTest(TestCase):

  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='testpassword')

  def test_login_page_status_code(self):
    response = self.client.get(reverse('login'))
    self.assertEqual(response.status_code, 200)

  def test_login(self):
    response = self.client.post(reverse('login'), data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow=True)
    self.assertTrue(response.context['user'].is_authenticated)

class LogoutTest(TestCase):

  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='testpassword')
    self.client.login(username='testuser', password='testpassword')

  def test_logout(self):
    # User should be logged in now
    self.assertTrue(self.user.is_authenticated)

    # Performing logout
    response = self.client.get(reverse('logout'))

    # Check if user is now logged out
    response = self.client.get('/')
    self.assertFalse(response.context['user'].is_authenticated)