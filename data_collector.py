import logging
import requests
import datetime
import boto3
import json

from config import BUCKET
from config import GBFS_URL


logging.basicConfig(encoding='utf-8', level=logging.INFO)


def get_station_information():
    resp = requests.get('%s/station_information.json' % GBFS_URL)
    data = resp.json()
    return data


def get_station_status():
    resp = requests.get('%s/station_status.json' % GBFS_URL)
    data = resp.json()
    return data


def get_available_bikes():
    resp = requests.get('%s/free_bike_status.json' % GBFS_URL)
    data = resp.json()
    return data


def get_aggregated_stations():
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(BUCKET, 'stations.json')
        data = json.loads(obj.get()['Body'].read().decode('utf-8'))
        return data
    except:
        return []


def write_aggregated_stations(stations):
    client = boto3.client('s3')
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(BUCKET, 'stations.json')
        obj.put(Body=json.dumps(stations))
    except Exception as exc:
        logging.error('%s' % str(exc))
        client.put_object(
            Body=json.dumps(stations),
            Bucket=BUCKET,
            Key='stations.json'
        )


def write_available_bike_count(count):
    data = {"count": count}
    now = datetime.datetime.utcnow()
    data['dt'] = '%s-%s-%sT%s:%s:%sZ' % (
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second
    )

    file = 'available_bikes/%s/%s/%s.json' % (
        now.year,
        now.month,
        now.day
    )

    client = boto3.client('s3')
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(BUCKET, file)
        content = obj.get()['Body'].read().decode('utf-8')
        todays_data = json.loads(content)
        todays_data.append(data)
        obj.put(Body=json.dumps(todays_data))
    except Exception as exc:
        logging.error('%s' % str(exc))
        todays_data = []
        todays_data.append(data)
        client.put_object(
            Body=json.dumps(todays_data),
            Bucket=BUCKET,
            Key=file
        )


def write_station_data(station_id, data):
    now = datetime.datetime.utcnow()
    data['dt'] = '%s-%s-%sT%s:%s:%sZ' % (
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second
    )

    file = '%s/%s/%s/%s.json' % (
        station_id,
        now.year,
        now.month,
        now.day
    )

    client = boto3.client('s3')
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(BUCKET, file)
        content = obj.get()['Body'].read().decode('utf-8')
        todays_data = json.loads(content)
        todays_data.append(data)
        obj.put(Body=json.dumps(todays_data))
    except Exception as exc:
        logging.error('%s' % str(exc))
        todays_data = []
        todays_data.append(data)
        client.put_object(
            Body=json.dumps(todays_data),
            Bucket=BUCKET,
            Key=file
        )


def main(ctx, evt):
    try:
        logging.info("Fetching Beryl Stations Data Feed...")
        beryl_stations = get_station_information()
        local_stations = get_aggregated_stations()

        for station in beryl_stations['data']['stations']:
            station_id = station.get('station_id')
            found = False
            for local_station in local_stations:
                if local_station['station_id'] == station_id:
                    found = True

            if not found:
                logging.info("Station not seen yet, adding.")
                local_stations.append(station)
            else:
                logging.info("Station already seen, skipping.")

        write_aggregated_stations(local_stations)


        logging.info("Updating counts for each station...")
        station_status = get_station_status()
        station_statuses = station_status['data']['stations']

        for local_station in local_stations:
            station_id = local_station.get('station_id')
            try:
                selected_station = None
                for station in station_statuses:
                    if station['station_id'] == station_id:
                        selected_station = station
                data = {
                    "bikes_available": selected_station['num_bikes_available'],
                    "docks_available": selected_station['num_docks_available']
                }
                logging.info("Writing station %s" % station_id)
                write_station_data(station_id, data)
            except Exception as err:
                logging.error("Error updating station %s" % station_id)


        logging.info("Counting available bikes...")
        bikes = get_available_bikes()
        available_bike_count = len(bikes['data']['bikes'])
        write_available_bike_count(available_bike_count)

    except Exception as err:
        logging.error("Error occurred: %s" % str(err))


if __name__ == '__main__':
    main({}, {})
