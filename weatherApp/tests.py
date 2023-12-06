from django.test import TestCase, Client
from .models import Event, UserSetting, Location
from .views import *
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from .forms import ChangeLocationForm, CustomUserCreationForm
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime, timedelta


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
    self.user = User.objects.create_user(username='testuser',
                                         password='testpassword')
    self.client.login(username='testuser', password='testpassword')
    Event.objects.create(title="Test Event",
                         description="Test Description",
                         start=datetime(2023, 11, 8, 10, 15, 0),
                         end=datetime(2023, 11, 8, 12, 30, 0),
                         user=self.user)

  def test_index_view(self):
    # reverse index view and assert that it gets back 200 responce
    response = self.client.get(reverse('index'))
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # assert that the page contains new event
    self.assertContains(
        response,
        '<li class="w3-hover-light-grey">Test Event - Nov. 8, 2023, 10:15 a.m. to Nov. 8, 2023, 12:30 p.m.</li>'
    )
    self.assertQuerysetEqual(response.context['event_list'],
                             ['<Event: Test Event>'],
                             ordered=False)

  def test_allEvents_view(self):
    # similar to previous test, but for allEvents view
    response = self.client.get(reverse('allEvents'))
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertContains(
        response,
        '<li class="w3-hover-light-grey">Test Event - Nov. 8, 2023, 10:15 a.m. to Nov. 8, 2023, 12:30 p.m.</li>'
    )
    self.assertQuerysetEqual(response.context['event_list'],
                             ['<Event: Test Event>'],
                             ordered=False)


class UserSettingViewTest(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(username='testuser',
                                         password='testpassword')
    self.client.login(username='testuser', password='testpassword')
    UserSetting.objects.create(user=self.user, weather_notifs="Enabled")

  def test_userSetting(self):
    # reverse view and assert that it gets back 200 response
    response = self.client.get(reverse('editUserSetting'))
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # assert that the page contains weather notification preference
    self.assertContains(response, 'Enabled')

  def test_changeUserSetting(self):
    # try and post a new weather notification preference
    response = self.client.post(reverse('editUserSetting'),
                                data={'weather_notifs': 'Disabled'})
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # assert that the page contains weather notification preference
    self.assertContains(response, 'Disabled')


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
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_signup_form(self):
    response = self.client.post(reverse('signup'),
                                data={
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
    self.user = User.objects.create_user(username='testuser',
                                         password='testpassword')

  def test_login_page_status_code(self):
    response = self.client.get(reverse('login'))
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  def test_login(self):
    response = self.client.post(reverse('login'),
                                data={
                                    'username': 'testuser',
                                    'password': 'testpassword'
                                },
                                follow=True)
    self.assertTrue(response.context['user'].is_authenticated)


class LogoutTest(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(username='testuser',
                                         password='testpassword')
    self.client.login(username='testuser', password='testpassword')

  def test_logout(self):
    # User should be logged in now
    self.assertTrue(self.user.is_authenticated)

    # Performing logout
    response = self.client.get(reverse('logout'))

    # Check if user is now logged out
    response = self.client.get('/')
    self.assertFalse(response.context['user'].is_authenticated)
class PasswordChangeTestCase(TestCase):

  def setUp(self):
    self.user = User.objects.create_user(username='testuser', email='test@example.com',   password='old_password')

  def test_password_change_view(self):
    self.client.login(username='testuser', password='old_password')
    response = self.client.get(reverse('password_change'))
    self.assertEqual(response.status_code, 200)
    self.assertTrue(isinstance(response.context['view'], auth_views.PasswordChangeView))

  def test_password_change_form(self):
    self.client.login(username='testuser', password='old_password')
    response = self.client.post(reverse('password_change'), {
        'old_password': 'old_password',
        'new_password1': 'new_password123',
        'new_password2': 'new_password123',
    })
    # Check redirection after successful password change
    self.assertRedirects(response, reverse('password_change_done'))

    # Verify password has been changed
    self.user.refresh_from_db()
    self.assertTrue(self.user.check_password('new_password123'))

class SettingsViewTest(TestCase):
  def test_get_page(self):
    response = self.client.get(reverse('settings'))
    self.assertEqual(response.status_code, status.HTTP_200_OK)



# tests added by Daniel for statment line coverage 
class IndexViewTest(TestCase):

    def setUp(self):
        # Setup test data
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Event.objects.create(title="Test Event",
         description="Test Description",
         start=datetime(2023, 11, 8, 10, 15, 0),
         end=datetime(2023, 11, 8, 12, 30, 0),
         user=self.user)

    def test_index_view_anonymous(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Log In, Sign Up, or Change Location', response.context['weather_data'])

    def test_index_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class EventModelViewSetTest(APITestCase):

  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='password')
    self.event = Event.objects.create(title="Test Event",
       description="Test Description",
       start=datetime(2023, 11, 8, 10, 15, 0),
       end=datetime(2023, 11, 8, 12, 30, 0),
       user=self.user)
    self.client.force_authenticate(user=self.user)  # If authentication is required

  def test_get_event_list(self):
    response = self.client.get(reverse('event-list'))  # URL name for the event list
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data), 1)  # Assuming only one event is created

  def test_get_event_detail(self):
    response = self.client.get(reverse('event-detail', args=[self.event.id]))  # URL name for event detail
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['title'], 'Test Event')

class ChangeLocationViewTest(TestCase):

  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='password')
    self.client.login(username='testuser', password='password')
    Location.objects.create(city='Indianapolis', state="IN", user=self.user)

  def test_location_get(self):
    response = self.client.get(reverse('changeLocation')) 
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.context['form'], ChangeLocationForm)

  def test_location_post(self):
    response = self.client.post(reverse('changeLocation'), {
        'city': 'Indianapolis',
        'state': 'IN'
    })
    self.assertEqual(response.status_code, 302)  # Assuming it redirects
    location = Location.objects.first()
    self.assertEqual(location.city, 'Indianapolis')
    self.assertEqual(location.state, 'IN')

class EventModelViewSetTest(APITestCase):

  def setUp(self):
    self.user = User.objects.create_user(username='testuser', password='password')
    self.event = Event.objects.create(title="Test Event",
       description="Test Description",
       start=datetime(2023, 11, 8, 10, 15, 0),
       end=datetime(2023, 11, 8, 12, 30, 0),
       user=self.user)
    self.client.force_authenticate(user=self.user)

  def test_get_event_list(self):
    response = self.client.get(reverse('event-list'))  
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data), 1)  # Assuming only one event is created

  def test_get_event_detail(self):
    response = self.client.get(reverse('event-detail', args=[self.event.id]))  
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['title'], 'Test Event')

class GetHazardousEventsTest(TestCase):

  def setUp(self):
    # Setup test data
    self.user = User.objects.create_user(username='testuser', password='testpassword')
    self.event = Event.objects.create(
        title="Test Event",
        start=datetime(2023, 11, 8, 10, 15, 0),
        end=datetime(2023, 11, 8, 12, 30, 0),
        user=self.user
    )
    UserSetting.objects.create(user=self.user, weather_notifs='Enabled')

  def test_get_hazardous_events(self):
    # Mock weather data
    start=datetime(2023, 11, 8, 10, 15, 0)
    end=datetime(2023, 11, 8, 12, 30, 0)
    mock_weather = {
        'periods': [
            {
                'startTime': start,
                'endTime': end,
                'windSpeed': "20 mph",
                'temperature': 45,
                'probabilityOfPrecipitation': {'value': 10},
                'icon': 'test_icon_url'
            }
            # Add more periods as needed to test different scenarios
        ]
    }

    hazardous_events = get_hazardous_events(self.user, mock_weather)

    # Check if the event is correctly identified as hazardous
    self.assertEqual(len(hazardous_events), 1)
    self.assertEqual(hazardous_events[0]['event'], self.event)
    self.assertEqual(hazardous_events[0]['icon'], 'test_icon_url')

  def test_get_hazardous_events_no_match(self):
    # Mock weather data where the event is not in range
    mock_weather = {
        'periods': [
            {
                'startTime': datetime(2023, 11, 8, 10, 15, 0),
                'endTime': datetime(2023, 11, 8, 12, 30, 0),
                'windSpeed': "20 mph",
                'temperature': 45,
                'probabilityOfPrecipitation': {'value': 10},
                'icon': 'test_icon_url'
            }
        ]
    }

    hazardous_events = get_hazardous_events(self.user, mock_weather)

    # Check if no hazardous events are identified
    self.assertEqual(len(hazardous_events), 0)