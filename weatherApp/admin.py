from django.contrib import admin
from .models import Event, Location, UserSetting

admin.site.register(Event)
admin.site.register(Location)
admin.site.register(UserSetting)
