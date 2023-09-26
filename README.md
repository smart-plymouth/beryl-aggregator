# Beryl Bike Aggregator
This service aggregates real time Beryl bike availability data from the Beryl GBFS API 
(https://gbfs.beryl.cc/v2_2/Plymouth/gbfs.json) and makes time series data available via an API.
The data is collected by a Lambda function which parses data from the Beryl API, this is triggered
by Event Bridge every 10 minutes. Retrieved data is stored within an S3 bucket and then
served by an API also hosted via Lambda and API Gateway.

## API Endpoint
* https://berylitics.api.smartplymouth.org

## API Routes
### /stations
Returns a list of Beryl bike stations the aggregator has seen.

#### Example Request
```curl 'https://berylitics.api.smartplymouth.org/stations' | jq```

#### Example Response
```
[
  {
    "capacity": 6,
    "lat": 50.396415,
    "lon": -4.141369,
    "name": "Torr Lane Supermarket",
    "rental_uris": {
      "android": "https://beryl.app/gbfs?$deeplink_path=gbfs_bay&bay_id=6815&scheme_id=23",
      "ios": "https://beryl.app/gbfs?$deeplink_path=gbfs_bay&bay_id=6815&scheme_id=23"
    },
    "station_id": 6815
  },
  {
    "capacity": 8,
    "lat": 50.3885,
    "lon": -4.109999,
    "name": "Torridge Way",
    "rental_uris": {
      "android": "https://beryl.app/gbfs?$deeplink_path=gbfs_bay&bay_id=6817&scheme_id=23",
      "ios": "https://beryl.app/gbfs?$deeplink_path=gbfs_bay&bay_id=6817&scheme_id=23"
    },
    "station_id": 6817
  },
  ...
]
```

### /stations/<station_id>
Returns the station meta-data and time series data for available bikes for the given station.
Optionally start and end query string args may be sent with the request to request a custom date range of data using ISO formatted dates.

e.g. ?start=2023-09-25&end=2023-09-26

#### Example Request
```curl 'https://berylitics.api.smartplymouth.org/stations/6867' | jq```

#### Example Response
```
{
  "lat": 50.387873,
  "lon": -4.139998,
  "name": "Peverell Park Road (South)",
  "rental_uris": {
    "android": "https://beryl.app/gbfs?$deeplink_path=gbfs_bay&bay_id=6867&scheme_id=23",
    "ios": "https://beryl.app/gbfs?$deeplink_path=gbfs_bay&bay_id=6867&scheme_id=23"
  },
  "station_id": 6867,
  "capacity": 4,
  "data": [
    {
      "bikes_available": 9,
      "docks_available": 4,
      "dt": "2023-9-25T0:0:0Z"
    },
    {
      "bikes_available": 9,
      "docks_available": 4,
      "dt": "2023-9-25T0:10:0Z"
    },
    {
      "bikes_available": 8,
      "docks_available": 4,
      "dt": "2023-9-25T0:20:0Z"
    },
    ...
  ]
}
```

### /bikes_available
Returns time series data of available bike count for the entire city. Optionally start and end query string args may be sent with the request to request a custom date range of data using ISO formatted dates.

e.g. ?start=2023-09-25&end=2023-09-26

#### Example Request
```curl 'https://berylitics.api.smartplymouth.org/available_bikes' | jq```

#### Example Reponse
```
[
  {
    "count": 303,
    "dt": "2023-9-26T10:49:52Z"
  },
  {
    "count": 303,
    "dt": "2023-9-26T10:51:55Z"
  },
  {
    "count": 306,
    "dt": "2023-9-26T11:1:50Z"
  },
  {
    "count": 306,
    "dt": "2023-9-26T11:11:50Z"
  },
  ...
]
```
