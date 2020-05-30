import json
import discord
import requests
from geopy.geocoders import Nominatim
from noaa_sdk import noaa as nws

noaa = nws.NOAA()

points_headers = {
    'User-Agent': 'MLH RookieHacks Test Application. Used for Discord bot using Discord.py',
    'Accept': 'application/geo+json'
}

def geocode(client_location):
    geolocator = Nominatim(user_agent="MLH RookieHacks Test Application")
    location = geolocator.geocode(client_location)
    if location == None:
        return None
    loc = [location.latitude, location.longitude]
    return loc

def get_gridpoints(location):
    client_location = geocode(location)
    try:
        points = requests.get("https://api.weather.gov/points/{0[0]},{0[1]}".format(client_location), headers=points_headers)
    except:
        return None
    tmp = json.loads(points.text)
    tmp1 = tmp['properties']
    passed = [tmp1['gridX'], tmp1['gridY'], tmp1['relativeLocation']['properties']['city'], tmp1['relativeLocation']['properties']['state'], tmp1['cwa'], client_location[0], client_location[1]]
    return passed

def getForecast(location):
    client_location = geocode(location)
    if client_location == None:
        return None
    lat, lon = client_location
    forecast = noaa.points_forecast(lat, lon, hourly=False)
    tmp1 = forecast['properties']['periods']
    return tmp1

def getAlerts(location):
    alerts = requests.get("https://api.weather.gov/alerts/active/area/{0}".format(location), headers=points_headers)
    tmp = json.loads(alerts.text)
    return tmp