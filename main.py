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


@app.route('getAddressImages')
def getImages(lat,lon):
    # SaveLoc = "./"
    #
    # fi = SaveLoc+lat + ".jpg"
    # # urllib.urlretrieve("www.google.com/imgres?imgurl=https%3A%2F%2Fcdn.pixabay.com%2Fphoto%2F2015%2F04%2F19%2F08%2F33%2Fflower-729512__340.jpg&imgrefurl=https%3A%2F%2Fpixabay.com%2Fimages%2Fsearch%2Fflowers%2F&tbnid=HQBoN3hx1MnYjM&vet=12ahUKEwibuKGz3rn6AhUsktgFHQaPAUwQMygHegUIARDrAQ..i&docid=6QnaOLvEQovLfM&w=514&h=340&q=flower%20images&ved=2ahUKEwibuKGz3rn6AhUsktgFHQaPAUwQMygHegUIARDrAQ", fi)
    # urllib.urlretrieve("http://www.gunnerkrigg.com//comics/00000001.jpg", "00000001.jpg")
    return "Hiiii"



if __name__ == '__main__':
    app.run(debug=True)
