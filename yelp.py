import time
import os
import os.path
import requests
import json
import pgeocode

from os import path

f = open("api.key", "r")
APIKEY = f.read().rstrip()

def fetch_results(lat, lng, rad, cat, limit, term):
    url = "https://api.yelp.com/v3/businesses/search?latitude={lat}&longitude={lng}&radius={rad}&categories={cat}&limit={limit}&term={term}".format(lat=lat,lng=lng, rad=rad,cat=cat,limit=limit, term=term)
    headers = {"Authorization" : APIKEY}

    response = requests.get(url, headers=headers)
    res = json.loads(response.text)

    return res["businesses"]

# Ask for some stuffs
# for reference, 15000 meters is about 9.5 miles
countryCode = input("2 character country code:")
zipCode = input("Postal Code:")
term = input("Search Term:")
rad = int(input("Radius in meters:"))

nomi = pgeocode.Nominatim(countryCode)
selectedArea = nomi.query_postal_code("45248")
startingLat = selectedArea["latitude"]
startingLng = selectedArea["longitude"]

# Converts meters to miles then multiplies by 69.172 to get the degrees (24901.92 miles cirumfrence of Equator / 360 degrees = 69.172 miles per degree)
varienceInDegrees = (rad / 1609.34) / 69.172
minLat = startingLat - varienceInDegrees
minLng = startingLng - varienceInDegrees
maxLat = startingLat + varienceInDegrees
maxLng = startingLng + varienceInDegrees
cat = "restaurants"
limit = 50


filename = "places.csv"
places = list()

print("Getting results for {cat} with search term {term}".format(cat=cat, term=term))
businesses = list()
""" This is to get a wider net and longer list, it searchs in a 3x3 grid pattern
    -x,+y   x,+y    +x,+y
    -x,y    x,y     +x,y
    -x,-y   x,-y    +x,-y
    x,y are the starting latitude and longitude
"""
businesses.append(fetch_results(startingLat, startingLng, rad, cat, limit, term))
businesses.append(fetch_results(minLat, startingLng, rad, cat, limit, term))
businesses.append(fetch_results(maxLat, startingLng, rad, cat, limit, term))
businesses.append(fetch_results(startingLat, minLng, rad, cat, limit, term))
businesses.append(fetch_results(startingLat, maxLng, rad, cat, limit, term))
businesses.append(fetch_results(minLat, minLng, rad, cat, limit, term))
businesses.append(fetch_results(minLat, maxLng, rad, cat, limit, term))
businesses.append(fetch_results(maxLat, minLng, rad, cat, limit, term))
businesses.append(fetch_results(maxLat, maxLng, rad, cat, limit, term))

for business in businesses:
    for result in business:
        if not any(x["name"] == result["name"] for x in places):
            places.append(result)


print("{count} places found.".format(count=len(places)))
print("Deleting old file")
if path.exists(filename):
    os.remove(filename)

print("Writing to file")
with open(filename, "w") as filehandle:
    for place in places:
        filehandle.write("\"" + str(place["name"]) + "\",\"" + str(place["url"]) + "\",\"" + str(place["distance"]) + "\",\"" + str(place["id"]) + "\"\n")


print("------------- Completed -------------")
