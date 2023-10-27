from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse

def index(request):
  return render(request, 'weatherApp/index.html')

      