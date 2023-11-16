# serializers.py in your app's directory

from rest_framework import serializers
from .models import Event  # replace with your model

class EventModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'  # List the fields you want to expose through the API
