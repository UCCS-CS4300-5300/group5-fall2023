from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, SignUpView
from django.contrib.auth import views as auth_views
from . import views
from .views import EventModelViewSet

router = DefaultRouter()
router.register(r'yourmodel', EventModelViewSet)

urlpatterns = [
  path("", views.index, name="index"),
  path("createEvent", views.createEvent, name="createEvent"),
  path("allEvents", views.allEvents, name="allEvents"),
  path('get_weather/', views.get_weather, name="get_weather"),
  path('headerBar', views.headerBar, name="headerBar"),
  path('login/', LoginView.as_view(), name='login'),
  path('signup/', SignUpView.as_view(), name='signup'),
  path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
  path('settings/', views.settings, name='settings'),
  path('settings/changeLocation/', views.changeLocation, name='changeLocation'),
  path('api/', include(router.urls)),
  ]
