from flask import Flask, render_template, redirect
import requests
import datetime
import configparser

app = Flask(__name__)

config = configparser.RawConfigParser()
config.read('config.txt')
key = config.get('Credentials', 'key')

@app.route('/')
def tracker_page():

    # Sedgwick (All)
    mapid = '40800' # 30156 (South)
    endpoint = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key={key}&mapid={mapid}&outputType=JSON".format(key=key, mapid=mapid)
    response = requests.get(endpoint).json()#['ctatt']['eta']

    def getTime(input_str):
        time_diff = datetime.datetime.strptime(input_str, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now()
        return round(time_diff.seconds / 60)

    def getRouteClass(rt):
        if rt == 'P':
            return "transit-rectangle-purple"
        elif rt == 'Brn':
            return "transit-rectangle-Brn"
        else:
            return "transit-rectangle-bus"

    train_info = [(x['rt'], x['destNm'], getTime(x['arrT']),getRouteClass(x['rt'])) for x in response['ctatt']['eta']][0:5]
    return render_template('tracker.html',
                            train_list=train_info)
