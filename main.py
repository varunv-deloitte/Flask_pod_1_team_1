from flask import Flask, jsonify, request
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
    lat = response[0]["lat"]
    lon = response[0]["lon"]
    data = {"Lat": lat, "Lon": lon}
    return getImages(lat,lon)


@app.route('/getAddressImages')
def getImages(lat,lon):
    token = "C33AES3-DZ5MTPQ-PSMXB57-7M960HT"
    zoom=["55m","100m"]
    for z in zoom:
        maps_url = "https://www.google.com/maps/@%s,%s,%s/data=!3m1!1e3"%(lat,lon,z)
        URL = "https://shot.screenshotapi.net/screenshot";
        URL += "?token=%s&url=%s&delay=%d" % (token, maps_url, 4000)
        print(URL)

        # sending get request and saving the response as response object
        r = requests.get(url=URL)
        # extracting data in json format
        data = r.json()

        screenshot_url = data["screenshot"]
        # Call the API

        urllib.request.urlretrieve(screenshot_url, "%d%s%s.jpg"%(z,lat,lon))

    return screenshot_url



if __name__ == '__main__':
    app.run(debug=True)
