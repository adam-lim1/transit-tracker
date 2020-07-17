from flask import Flask, render_template, redirect
import requests
import datetime
import configparser
from pytz import timezone
from tzlocal import get_localzone

app = Flask(__name__)

# Read Config Parameters
config = configparser.RawConfigParser()
config.read('config.txt')
train_key = config.get('Credentials', 'train_key')
bus_key = config.get('Credentials', 'bus_key')

threshold_times = {}
threshold_times['Train'] = {'Yellow': config.get('Threshold Times', 'train_yellow'),
                            'Red': config.get('Threshold Times', 'train_red')}
threshold_times['Bus'] = {'Yellow': config.get('Threshold Times', 'bus_yellow'),
                            'Red': config.get('Threshold Times', 'bus_red')}

# Define Helpers
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

def getLocalTime(dt_obj_naive):
    """
    Convert naive datetime object from CDT/CST to %Y-%m-%dT%H:%M:%S format
    string of user's local time
    """
    chicago_dt_obj = timezone('America/Chicago').localize(dt_obj_naive)

    # Get user's local timezone
    local_tz = get_localzone()
    local_dt_obj = chicago_dt_obj.astimezone(local_tz)
    date_str_local = local_dt_obj.strftime("%Y-%m-%dT%H:%M:%S")

    return date_str_local

def getTrainTimestamp(train_arrival):
    """
    Given %Y-%m-%dT%H:%M:%S style string in Chicago timezone, get %Y-%m-%dT%H:%M:%S
    style string in user's local timezone
    """
    train_arrival_dt = datetime.datetime.strptime(train_arrival, "%Y-%m-%dT%H:%M:%S")
    local_train_arrival = getLocalTime(train_arrival_dt)
    return local_train_arrival

def getBusTimestamp(bus_arrival):
    """
    Convert output from Bus Tracker API to usable timestamp format in user's local
    timezone
    Ex: '20200326 14:04' -> '2020-03-26T14:04:00'
    """
    bus_arrival_dt = datetime.datetime.strptime(bus_arrival, "%Y%m%d %H:%M")
    local_bus_arrival = getLocalTime(bus_arrival_dt)
    return local_bus_arrival

@app.route('/')
def tracker_page():

    ####### TRAIN INFO #######
    mapid = '40800' # Sedgwick (All trains)
    endpoint = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key={key}&mapid={mapid}&outputType=JSON".format(key=train_key, mapid=mapid)
    response = requests.get(endpoint).json() #['ctatt']['eta']
    
    train_info = [[x['rt'], x['destNm'], getTrainTimestamp(x['arrT']), getRouteClass(x['rt'])] for x in response['ctatt']['eta']][0:4] # First 4 entries

    # Add JavaScript ID for time countdown
    for i in range(0, len(train_info)):
        train_info[i].append("train{}".format(i+1))

    #print(train_info)

    ####### BUS INFO #######

    stpid = 927 # North Ave / Sedgwick (Northeast Corner)
    rt = 72
    endpoint = "http://www.ctabustracker.com/bustime/api/v2/getpredictions?key={key}&stpid={stpid}&rt={rt}&format=json".format(key=bus_key, stpid=stpid, rt=rt)
    response = requests.get(endpoint)
    response = response.json()['bustime-response']['prd']
    #response = [{'tmstmp': '20200223 21:36', 'typ': 'A', 'stpnm': 'North Avenue & Sedgwick', 'stpid': '927', 'vid': '8235', 'dstp': 1797, 'rt': '72', 'rtdd': '72', 'rtdir': 'Westbound', 'des': 'Harlem', 'prdtm': '20200223 21:42', 'tablockid': '72 -810', 'tatripid': '1010106', 'dly': False, 'prdctdn': '6', 'zone': ''}]
    bus_info = [[x['des'], getBusTimestamp(x['prdtm'])] for x in response][0:2]

    # Add JavaScript ID for time countdown
    for i in range(0, len(bus_info)):
        bus_info[i].append("bus{}".format(i+1))

    #print(bus_info)

    ####### RETURN INFO #######

    return render_template('tracker.html',
                            train_list=train_info,
                            bus_list=bus_info,
                            threshold_times=threshold_times)
