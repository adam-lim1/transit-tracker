from flask import Flask, render_template, redirect
import requests
import datetime
import configparser

app = Flask(__name__)

config = configparser.RawConfigParser()
config.read('config.txt')
train_key = config.get('Credentials', 'train_key')
bus_key = config.get('Credentials', 'bus_key')


def getTrainTime(input_str):
    """
    Return number of minutes until train is due
    """
    time_diff = datetime.datetime.strptime(input_str, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now()
    return round(time_diff.seconds / 60)

def getRouteClass(rt):
    """
    Dynamically define CSS class named based on Train route
    """
    if rt == 'P':
        return "transit-rectangle-purple"
    elif rt == 'Brn':
        return "transit-rectangle-Brn"
    else:
        return "transit-rectangle-bus"

def getBusTime(input_str):
    """
    Return number of minutes until bus is due
    """
    time_diff = datetime.datetime.strptime(input_str, "%Y%m%d %H:%M") - datetime.datetime.now()
    return round(time_diff.seconds / 60)

@app.route('/')
def tracker_page():

    ####### TRAIN INFO #######
    mapid = '40800' # Sedgwick (All trains)
    endpoint = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key={key}&mapid={mapid}&outputType=JSON".format(key=train_key, mapid=mapid)
    response = requests.get(endpoint).json() #['ctatt']['eta']

    train_info = [(x['rt'], x['destNm'], getTrainTime(x['arrT']),getRouteClass(x['rt'])) for x in response['ctatt']['eta']][0:5] # First 4 entries

    ####### BUS INFO #######

    stpid = 927 # North Ave / Sedgwick (Northeast Corner)
    rt = 72
    endpoint = "http://www.ctabustracker.com/bustime/api/v2/getpredictions?key={key}&stpid={stpid}&rt={rt}&format=json".format(key=bus_key, stpid=stpid, rt=rt)
    response = requests.get(endpoint)
    response = response.json()['bustime-response']['prd']

    bus_info = [(x['des'], getBusTime(x['prdtm'])) for x in response[0:2]]

    ####### RETURN INFO #######

    return render_template('tracker.html',
                            train_list=train_info,
                            bus_list=bus_info)
