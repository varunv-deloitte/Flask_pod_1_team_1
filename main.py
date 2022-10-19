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


    URL = "https://shot.screenshotapi.net/screenshot?token=C33AES3-DZ5MTPQ-PSMXB57-7M960HT&url=https://www.google.com/maps/@28.5434542,77.2855899,400m/data=!3m1!1e3&delay=4000";
    # sending get request and saving the response as response object
    r = requests.get(url=URL)

    # extracting data in json format
    data = r.json()

    screenshot_url = data["screenshot"]
    # Call the API

    urllib.request.urlretrieve(screenshot_url, "00000007.jpg")

    return screenshot_url


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
    token = "NT8SXP4-BDHM3VM-PC5NCZN-3C6X4M7"
    # url = urllib.parse.quote_plus("https://google.com")
    # width = 1920
    # height = 1080
    # output = "image"
    # Construct the query params and URL
    # query = "https://shot.screenshotapi.net/screenshot"
    # query += "?token=%s&url=%s&width=%d&height=%d&output=%s" % (token, url, width, height, output)
    query = "https://shot.screenshotapi.net/screenshot?token=NT8SXP4-BDHM3VM-PC5NCZN-3C6X4M7&url=https://apple.com";
    # Call the API
    urllib.request.urlretrieve(query, "./screenshot.png")
    return "Hii"
    # print("Image")
    # urllib.request.urlretrieve("http://www.gunnerkrigg.com//comics/00000001.jpg", "00000001.jpg")
    # return "Hiiii"



if __name__ == '__main__':
    app.run(debug=True)
