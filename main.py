from flask import Flask, jsonify, request
import requests
import urllib.parse
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'


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
    print("Image")
    urllib.request.urlretrieve("http://www.gunnerkrigg.com//comics/00000001.jpg", "00000001.jpg")
    return "Hiiii"



if __name__ == '__main__':
    app.run(debug=True)
