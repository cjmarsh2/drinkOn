import urllib.request
import json
import googlemaps
from datetime import datetime
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import HappyhourForm
import uuid
import boto3
from ..models import Happyhour, Photo
import os
import requests

IPSTACKKEY = os.environ['IP_STACK_API']
GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
GMAPS = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'happyhourwdi'

data = requests.get("http://iatacodes.org/api/v6/cities?api_key=c05152c1-441f-430e-9c6c-54dca70f1427")
res = data.json()['request']

def happyhour_index(request):
  happyhourresults = Happyhour.objects.all()
  return render(request, 'happyhour/index.html', { 'happyhourresults': happyhourresults })

def happyhour_detail(request, happyhour_id):
  happyhour = Happyhour.objects.get(id=happyhour_id)
  happyhour_form = HappyhourForm()
  return render(request, 'happyhour/detail.html', { 
    'happyhour': happyhour,
    'happyhour_form': happyhour_form
  })

class HappyhourCreate(CreateView):
  model = Happyhour
  fields = '__all__'
  success_url = '/happyhour/'

class HappyhourUpdate(UpdateView):
  model = Happyhour
  fields = ['name', 'address', 'time_start', 'time_end', 'added']
  success_url = '/happyhour/'

# Not sure if we will need a delete form but included just in case
class HappyhourDelete(LoginRequiredMixin, DeleteView):
  model = Happyhour
  success_url = '/happyhour/'

def nearby(request):
  coordinates = _get_location()
  print_results = _display_nearby_places(_get_nearby_places(coordinates[0], coordinates[1]))
  restaurant_list = list(zip(print_results[0], print_results[1], print_results[2]))
  return render(request, 'nearby.html', {
    'restaurant_list': restaurant_list,
  })

def _get_location():
  location_latitude = res['client']['lat']
  location_longitude = res['client']['lng']
  return location_latitude, location_longitude

# def _get_location():
#   f = urllib.request.urlopen('http://api.ipstack.com/check?access_key=' + IPSTACKKEY)
#   json_string = f.read()
#   f.close()
#   location = json.loads(json_string)
#   location_latitude = location['latitude']
#   location_longitude = location['longitude']
#   return location_latitude, location_longitude

def _get_nearby_places(location_latitude, location_longitude):
  coordinates = (location_latitude, location_longitude)
  return GMAPS.places_nearby(
    location=coordinates,
    # rank_by='distance',
    type='restaurant',
    radius=5000
  )

def _display_nearby_places(nearby_json):
    resultsname = []
    resultsaddress =[]
    resultsid = []
    for result in nearby_json['results']:
        resultsname.append(result['name']),
        resultsaddress.append(result['vicinity'])
        resultsid.append(result['place_id'])
    return resultsname, resultsaddress, resultsid

def add_photo(request, happyhour_id):
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      photo = Photo(url=url, happyhour_id=happyhour_id)
      photo.save()
    except:
      print('An error occurred uploading file to S3')
  return redirect('detail', happyhour_id=happyhour_id)
