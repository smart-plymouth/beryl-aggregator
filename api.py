import boto3
import json
import datetime
import dateutil

from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from config import BUCKET


app = Flask(__name__)
CORS(app)


def get_stations():
    s3 = boto3.resource('s3')
    obj = s3.Object(BUCKET, 'stations.json')
    data = json.loads(obj.get()['Body'].read().decode('utf-8'))
    return data


def get_station_by_id(station_id):
    stations = get_stations()
    selected = None

    for station in stations:
        if station.get('station_id') == int(station_id):
            selected = station

    return selected


def get_data_by_range(resource, start_date, end_date):
    date_diff = end_date - start_date
    days_diff = date_diff.days
    data = []
    for x in range(0, days_diff + 1):
        current_date = start_date + datetime.timedelta(days=x)
        data.extend(get_data_by_date(resource, current_date))
    return data


def get_data_by_date(resource, date):
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(BUCKET, '%s/%s/%s/%s.json' % (
            resource,
            date.year,
            date.month,
            date.day
        ))
        data = json.loads(obj.get()['Body'].read().decode('utf-8'))
        return data
    except Exception:
        return []


@app.route('/stations')
def list_stations():
    stations = get_stations()
    return jsonify(stations)


@app.route('/stations/<string:station_id>')
def fetch_station_by_id(station_id):
    now = datetime.datetime.utcnow()

    station = get_station_by_id(station_id)
    if not station:
        return jsonify(
            {
                'error': 'Not Found',
                'status': 404,
                'message': 'Station not found.'
            }
        ), 404

    station['data'] = []

    start = request.args.get('start')
    if start:
        start_dt = dateutil.parser.parse(start)
    else:
        start_dt = now - datetime.timedelta(hours=24)

    end = request.args.get('end')
    if end:
        end_dt = dateutil.parser.parse(end)
    else:
        end_dt = now

    if end_dt < start_dt:
        return jsonify(
            {
                'error': 'Bad Request',
                'status': 400,
                'message': 'End date must be after start date.'
            }
        ), 400

    data = get_data_by_range(station_id, start_dt, end_dt)
    station['data'].extend(data)

    return jsonify(station)


@app.route('/available_bikes')
def get_available_bike_counts():
    resource = 'available_bikes'
    now = datetime.datetime.utcnow()

    results = []

    start = request.args.get('start')
    if start:
        start_dt = dateutil.parser.parse(start)
    else:
        start_dt = now - datetime.timedelta(hours=24)

    end = request.args.get('end')
    if end:
        end_dt = dateutil.parser.parse(end)
    else:
        end_dt = now

    if end_dt < start_dt:
        return jsonify(
            {
                'error': 'Bad Request',
                'status': 400,
                'message': 'End date must be after start date.'
            }
        ), 400

    data = get_data_by_range(resource, start_dt, end_dt)
    results.extend(data)

    return jsonify(results)


@app.route("/")
def get_app_version():
    app_data = {
        "service": "Berylitics API",
        "version": 1.0
    }
    return jsonify(app_data)
