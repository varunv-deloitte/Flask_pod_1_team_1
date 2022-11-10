from flask import Flask, request, jsonify, make_response, session, redirect, url_for
import requests
import urllib.parse
from bs4 import BeautifulSoup
import psycopg2
import os
import urllib.request
import ssl
import addfips
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Initialize
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = "asddaffffa"
load_dotenv()

# bcrypt = Bcrypt(app)
ssl._create_default_https_context = ssl._create_unverified_context

# DB connection
DB_URL = os.getenv("DB_URL")
AWS_ACCESS_KEY= os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS= os.getenv("AWS_SECRET_ACCESS_ID")
connection = psycopg2.connect(DB_URL)

# DB query
CREATE_USER_TABLE = "CREATE TABLE IF NOT EXISTS client (id SERIAL PRIMARY KEY, name TEXT, email TEXT, password TEXT);"

INSERT_USER_DATA = "INSERT INTO client (name,email,password) VALUES (%s, %s, %s) RETURNING id,name,email;"

FIND_USER_IN_DB = "SELECT * FROM client WHERE email=(%s);"


# Helper functions
def getNRI_Code(s, c):
    af = addfips.AddFIPS()
    x = af.get_county_fips(c, state=s)
    return "c" + str(x)


def validatePassword(hashPassword, password):
    print(hashPassword,password)
    return bcrypt.check_password_hash(hashPassword, password)

def uploadtos3(bucket_name,file_path,k):
    from botocore.config import Config
    # !pip install boto3
    import boto3 # pip install boto3
    my_config = Config(region_name = 'ap-south-1')
    # Let's use Amazon S3
    s3 = boto3.resource("s3",config=my_config,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_ACCESS)
    # Print out bucket names
    s3 = boto3.client("s3",config=my_config,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key= AWS_SECRET_ACCESS)
    s3.upload_file(
    Filename=file_path,
    Bucket=bucket_name,
    Key=k
    )

def downloadfroms3(bucket_name,k,path_to_store):
    from botocore.config import Config
    # !pip install boto3
    import boto3 # pip install boto3
    my_config = Config(region_name = 'ap-south-1')
    # Let's use Amazon S3
    s3 = boto3.resource("s3",config=my_config,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_ACCESS)
    # Print out bucket names
    s3 = boto3.client("s3",config=my_config,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_ACCESS)
    s3.download_file(Bucket=bucket_name, Key=k, Filename=path_to_store)


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
        # uploadtos3("property-images-bucket","./"+image_url,image_url)
        # downloadfroms3("property-images-bucket", "best (4).pt", "./S3images/best (4).pt")

    return "Image retrieved successfully "


@app.route("/getnearByplace", methods=['POST'])
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
            email = data["email"]
            password = data["password"]
            if not name or not email or not password:
                return {"message": "All fields are required ", "auth": False, "isUser": False}, 404

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
            email = data["email"]
            password = data["password"]

            if not email or not password:
                return {"message":"All fields are required ","auth": False, "isUser":False}, 404

            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(FIND_USER_IN_DB, (email,))
                    isUser = cursor.fetchone()

                    if not isUser:
                        return {"message": "User not registered in DB", "auth": False, "isUser":False}, 404
                    else:

                        user_password_hash = isUser[3]
                        print(check_password_hash(user_password_hash, password))
                        if check_password_hash(user_password_hash, password):
                            session['email']=isUser[2]
                            return {"auth":True, "isUser":True,  "user":{
                                "name":isUser[1],
                                "email":isUser[2]
                            }}, 200
                        else:
                            return {"message": "User password couldn't match", "auth": False, "isUser":True}, 404

        except:
            return "Login failed"


if __name__ == '__main__':
    app.run(debug=True)
