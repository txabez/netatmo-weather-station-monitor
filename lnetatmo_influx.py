#!/usr/bin/env python3
# encoding=utf-8

import lnetatmo
from influxdb import InfluxDBClient

NETATMO_CLIENT_ID = ''
NETATMO_CLIENT_SECRET = ''
NETATMO_USERNAME = ''
NETATMO_PASSWORD = ''

DB_HOST = 'db.netatmo.txabez.org'
DB_PORT = 8086
DB_USER = 'netatmo'
DB_PASS = 'secretpassword'
DB_NAME = 'netatmo'

authorization = lnetatmo.ClientAuth(
        clientId=NETATMO_CLIENT_ID,
        clientSecret=NETATMO_CLIENT_SECRET,
        username=NETATMO_USERNAME,
        password=NETATMO_PASSWORD,
        scope='read_station'
        )

weatherData = lnetatmo.WeatherStationData(authorization)

client = InfluxDBClient(host=DB_HOST, port=DB_PORT, username=DB_USER, password=DB_PASS, database=DB_NAME)
if {'name': 'netatmo'} not in client.get_list_database():
    client.create_database('netatmo')

for station in weatherData.stations:
    station_data = []
    module_data = []
    station = weatherData.stationById(station)
    station_name = station['station_name']
    altitude = station['place']['altitude']
    country= station['place']['country']
    timezone = station['place']['timezone']
    longitude = station['place']['location'][0]
    latitude = station['place']['location'][1]
    for module, moduleData in weatherData.lastData().items():
        for measurement in ['altitude', 'country', 'longitude', 'latitude', 'timezone']:
            value = eval(measurement)
            if type(value) == int:
                value = float(value)
            station_data.append({
                "measurement": measurement,
                "tags": {
                    "station": station_name,
                    "module": module
                },
                "time": moduleData['When'],
                "fields": {
                    "value": value
                }
            })

        for sensor, value in moduleData.items():
            if sensor.lower() != 'when':
                if type(value) == int:
                    value = float(value)
                module_data.append({
                    "measurement": sensor.lower(),
                    "tags": {
                        "station": station_name,
                        "module": module
                    },
                    "time": moduleData['When'],
                    "fields": {
                        "value": value
                    }
                })

    client.write_points(station_data, time_precision='s', database='netatmo')
    client.write_points(module_data, time_precision='s', database='netatmo')
