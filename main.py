from flask import Flask
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/getgeocode')
def getGeoCode():
    return "hi"

if __name__ == '__main__':
    app.run()
