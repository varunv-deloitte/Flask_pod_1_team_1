from flask import Flask, request
import requests
import urllib.parse

import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello!!!!!!!!"


@app.route('/getUserAddress', methods=['POST'])
def getAddress():
    if request.method == 'POST':
        try:
            address = request.json['address']
            return getGeoCode(address)
        except:
            return "Please Pass the valid address"

    return "Hii"


@app.route('/getgeocode/<address>')
def getGeoCode(address):
    # address = '985 Sterling Pl, Brooklyn, NY 11213, USA'
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()
    print(response)
    lat = response[0]["lat"]
    lon = response[0]["lon"]
    data = {"Lat": lat, "Lon": lon}
    return getImages(lat, lon)


@app.route('/getAddressImages')
def getImages(lat, lon):
    print(lat, lon)
    token = "C33AES3-DZ5MTPQ-PSMXB57-7M960HT"
    zoom = [43, 111]
    for z in zoom:
        maps_url = "https://www.google.com/maps/@%s,%s,%dm/data=!3m1!1e3" % (lat, lon, z)
        URL = "https://shot.screenshotapi.net/screenshot";
        URL += "?token=%s&url=%s&delay=%d" % (token, maps_url, 4000)
        # sending get request and saving the response as response object
        r = requests.get(url=URL)

        # extracting data in json format
        data = r.json()

        screenshot_url = data["screenshot"]
        # Call the API

        urllib.request.urlretrieve(screenshot_url, "%d%s%s.jpg" % (z, lat, lon))

    return "Image retrieved successfully "

@app.route("/getnearByplace", methods=['POST'])
def getNearByPlace():
    if request.method == 'POST':
        try:
            lat = request.json['lat']
            lan = request.json['lan']
            radius = request.json['radius']
            categories = request.json['categories']
            apiKey='71e7c3f7389e451fad669ee1ca43b8da'
            print(lat,lan,radius,categories)
            nearByPlaceUrl = "https://api.geoapify.com/v2/places?categories=%s&filter=circle:%s,%s,%d&bias=proximity:%s,%s&limit=20&apiKey=%s" %(categories,lan,lat,radius,lan,lat,apiKey)
            print(nearByPlaceUrl)
            nearByplaces = requests.get(nearByPlaceUrl)
            data = nearByplaces.json()
            print(data)
            return data
        except:
            return "Falild to featch places"


if __name__ == '__main__':
    app.run(debug=True)