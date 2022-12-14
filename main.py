# Common import
import os
# from yolov5.mlmodel import detect
from segmentation import get_yolov5
import functools
import re
import torch
from PIL import Image
import io
import json
import cv2

# Backend import
from flask import Flask, request, jsonify, make_response, session, redirect, url_for
import requests
import urllib.parse
from bs4 import BeautifulSoup
import psycopg2
import urllib.request
import ssl
import addfips
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# ML model import
import argparse
import sys
from pathlib import Path

import torch
import torch.backends.cudnn as cudnn

#
# from models.common import DetectMultiBackend
# from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
# from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
#                            increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
# from utils.plots import Annotator, colors, save_one_box
# from utils.torch_utils import select_device, time_sync


load_dotenv()

# env variables
DB_URL = os.getenv("DB_URL")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS = os.getenv("AWS_SECRET_ACCESS_ID")
SECRET = os.getenv("SECRET")

# Initialize
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = SECRET

model = get_yolov5()
ssl._create_default_https_context = ssl._create_unverified_context

# DB connection
connection = psycopg2.connect(DB_URL)

# DB query
CREATE_USER_TABLE = "CREATE TABLE IF NOT EXISTS client (id SERIAL PRIMARY KEY, name TEXT, email TEXT, password TEXT);"

INSERT_USER_DATA = "INSERT INTO client (name,email,password) VALUES (%s, %s, %s) RETURNING id,name,email;"

FIND_USER_IN_DB = "SELECT * FROM client WHERE email=(%s);"


# Helper functions
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)

    return secure_function


def getNRI_Code(s, c):
    af = addfips.AddFIPS()
    x = af.get_county_fips(c, state=s)
    return "c" + str(x)


def uploadtos3(bucket_name, file_path, k):
    from botocore.config import Config
    # !pip install boto3
    import boto3  # pip install boto3
    my_config = Config(region_name='ap-south-1')
    # Let's use Amazon S3
    s3 = boto3.resource("s3", config=my_config, aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_ACCESS)
    # Print out bucket names
    s3 = boto3.client("s3", config=my_config, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS)
    s3.upload_file(
        Filename=file_path,
        Bucket=bucket_name,
        Key=k
    )


def downloadfroms3(bucket_name, k, path_to_store):
    from botocore.config import Config
    # !pip install boto3
    import boto3  # pip install boto3
    my_config = Config(region_name='ap-south-1')
    # Let's use Amazon S3
    s3 = boto3.resource("s3", config=my_config, aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_ACCESS)
    # Print out bucket names
    s3 = boto3.client("s3", config=my_config, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS)
    s3.download_file(Bucket=bucket_name, Key=k, Filename=path_to_store)


# def detect():
# !python detect.py - -weights / content / gdrive / MyDrive / ml / best.pt - -img416 - -conf0.4 - -source.. / yolov5 / PropertyDataset / test / images - -hide - conf

@app.route('/')
def hello_world():
    return "Hello!!!!!!!!"


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method != "POST":
        return "Not"

    if request.files.get("image"):
        # Method 1
        # with request.files["image"] as f:
        #     im = Image.open(io.BytesIO(f.read()))

        # Method 2
        im_file = request.files["image"]
        im_bytes = im_file.read()
        input_image = Image.open(io.BytesIO(im_bytes))

        results = model(input_image, size=640)
        detect_res = results.pandas().xyxy[0].to_json(orient="records")  # JSON img1 predictions
        detect_res = json.loads(detect_res)
        # cv2.imwrite("./S3images", results.save())
        # results.save(save_dir="./S3images")
        # results.ims  # array of original images (as np array) passed to model for inference
        # results.render()  # updates results.ims with boxes and labels
        # print(results.render())
        # for im in results.ims:
        #     buffered = io.BytesIO()
        #     im_base64 = Image.fromarray(im)
        #     im_base64.save(buffered, format="JPEG")
        # for img in results.imgs:
        #     bytes_io = io.BytesIO()
        #     img_base64 = Image.fromarray(img)
        #     img_base64.save(bytes_io, format="jpeg")
        return {"result": detect_res}


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
    return getImages(lat, lon)


@app.route('/getAddressImages')
def getImages(lat, lon):
    print(lat, lon)
    token = "C33AES3-DZ5MTPQ-PSMXB57-7M960HT"
    zoom = [43]
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
        image_url = "%d%s%s.jpg" % (z, lat, lon)
        urllib.request.urlretrieve(screenshot_url, image_url)
        print(image_url)
        detect()
        # uploadtos3("property-images-bucket","./"+image_url,image_url)
        # downloadfroms3("property-images-bucket", "best (4).pt", "./S3images/best (4).pt")

    return "Image retrieved successfully "


@app.route("/getnearByplace", methods=['POST'])
# @login_required
def getNearByPlace():
    if request.method == 'POST':
        try:
            lat = request.json['lat']
            lan = request.json['lan']
            radius = request.json['radius']
            categories = request.json['categories']
            apiKey = '71e7c3f7389e451fad669ee1ca43b8da'
            nearByPlaceUrl = "https://api.geoapify.com/v2/places?categories=%s&filter=circle:%s,%s,%d&bias=proximity:%s,%s&limit=20&apiKey=%s" % (
                categories, lan, lat, radius, lan, lat, apiKey)
            nearByplaces = requests.get(nearByPlaceUrl)
            data = nearByplaces.json()
            return data
        except:
            return "Falild to featch places"


@app.route("/getriskindex", methods=['POST'])
# @login_required
def getRiskIndex():
    if request.method == 'POST':
        # try:
        state = request.json['state']
        county = request.json['county']
        data = getNRI_Code(state, county)

        FEMA_URL = "https://hazards.fema.gov/nri/report/viewer?dataLOD=Counties&dataIDs=%s" % (data)

        html_text = requests.get(FEMA_URL).text
        soup = BeautifulSoup(html_text, 'lxml')
        risk_score = soup.find('span', class_='summary-row-score-value').text
        risk_list = soup.find('div', class_='risk-list print-together')
        risk_list_score_list = risk_list.findAll('td', class_="number")
        risk_list_score_name = risk_list.findAll('td', class_='text')
        score = []
        heading = []

        f = 1
        for heading_list in risk_list_score_name:
            if f:
                heading.append(heading_list.text)
            f = (f + 1) % 2

        for score_list in risk_list_score_list:
            temp = score_list.find('span').text
            if (temp == '--'):
                temp = '0'
            score.append(temp)

        [text, value] = risk_score.split(" ")
        data = {"Risk_score": value}
        for i in range(min(len(score), len(heading))):
            data[heading[i]] = score[i]

        return make_response(jsonify(data), 200)


@app.route("/signup", methods=['POST'])
def createUser():
    if request.method == 'POST':
        try:
            data = request.get_json()
            name = data["name"]
            email = data["email"].lower()
            password = data["password"]

            regex_email = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            regex_password = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            pattern = re.compile(regex_password)
            isPassword = re.search(pattern, password)

            if not name.isalpha():
                return {"message": "Name should not contain numbers", "auth": False, "isUser": False}, 404

            if not name or not email or not password or not len(name) > 2:
                return {"message": "All fields are required ", "auth": False, "isUser": False}, 404

            if not re.fullmatch(regex_email, email):
                return {"message": "Enter the valid email", "auth": False, "isUser": False}, 404

            if not isPassword:
                return {"message": "Password Should be between 6 to 20 characters long and contain at least one uppercase,lowercase,special character and one number", "auth": False, "isUser": False}, 404


            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(CREATE_USER_TABLE)
                    cursor.execute(FIND_USER_IN_DB, (email,))
                    res_data = cursor.fetchone()
                    if res_data:
                        return {"message": "User already present in DB"}, 400
                    else:
                        _hashed_password = generate_password_hash(password)
                        cursor.execute(INSERT_USER_DATA, (name, email, _hashed_password))
                        res_data = cursor.fetchone()
            return {"id": res_data[0], "name": res_data[1], "email": res_data[2]}, 201

        except:
            return "Unable to Signup"


@app.route("/login", methods=['POST'])
def loginUser():
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data["email"].lower()
            password = data["password"]

            if not email or not password:
                return {"message": "All fields are required ", "auth": False, "isUser": False}, 404

            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(FIND_USER_IN_DB, (email,))
                    isUser = cursor.fetchone()

                    if not isUser:
                        return {"message": "User not registered in DB", "auth": False, "isUser": False}, 404
                    else:

                        user_password_hash = isUser[3]
                        print(check_password_hash(user_password_hash, password))
                        if check_password_hash(user_password_hash, password):
                            session['email'] = isUser[2]
                            return {"auth": True, "isUser": True, "user": {
                                "name": isUser[1],
                                "email": isUser[2]
                            }}, 200
                        else:
                            return {"message": "User password couldn't match", "auth": False, "isUser": True}, 404

        except:
            return "Login failed"


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for("/login"))


if __name__ == '__main__':
    app.run(debug=True)
