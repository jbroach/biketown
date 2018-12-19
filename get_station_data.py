"""Get GBFS-compliant station data and organize it."""

import requests
import csv
import json
import pyproj
import matplotlib.pyplot as plt
from math import ceil

def utm_from_latlng(lat, lon):
    """Returns correct EPSG code for a lat, lng point

    Note: Based on formula from https://tinyurl.com/y95ku6h4

    """
    EPSG = 32700 - round((45 + lat) / 90) * 100 + round((183 + lon) / 6)
    return EPSG

url = 'https://raw.githubusercontent.com/NABSA/gbfs/master/systems.csv'
r = requests.get(url)
rows = r.text.splitlines()
reader = csv.DictReader(rows)

us_systems = {}
n_sys = 0
for row in reader:
    if row['Country Code'] =='US':
        if row['Location'] not in us_systems:
            us_systems[row['Location']] = {}
        us_systems[row['Location']][row['Name']] = row
        n_sys += 1
print('{} systems in {} locations found'.format(n_sys, len(us_systems)))

# Get station feed data and store
#for loc in us_systems:
#    for sys in us_systems[loc]:
sysset = set(['BIKETOWN', 'Divvy', 'Citi Bike', 'Nice Ride Minnesota'])

plt.figure(figsize=(11, 8.5))
i = 0
for loc in us_systems:
    for sys in [s for s in us_systems[loc] if s in sysset]:
        epsg = None  # from calculated local UTM zone
        i += 1
        url = us_systems[loc][sys]['Auto-Discovery URL']
        print('{} {}'.format(sys, loc))
        r = requests.get(url).json()
        #rows = r.json()
        #reader = csv.DictReader(rows)
        status_url = next(item for item in r['data']['en']['feeds'] if
                          item['name'] == 'station_status')['url']
        info_url = next(item for item in r['data']['en']['feeds'] if
                        item['name'] == 'station_information')['url']
        status = requests.get(status_url).json()['data']['stations']
        stations = {}
        for station in [station for station in status if
                        station['is_installed'] == 1]:
            stations[station['station_id']] = {}
        print('...{} installed stations found'.format(len(stations)))
        info = requests.get(info_url).json()['data']['stations']
        for station in [station for station in info if
                        station['station_id'] in stations]:
            lat, lon = float(station['lat']), float(station['lon'])
            if not epsg:
                epsg = utm_from_latlng(lat, lon)
                print('epsg: {}'.format(epsg))
            x, y = pyproj.transform(pyproj.Proj(init='epsg:4326'),
                                    pyproj.Proj(init='epsg:{}'.format(epsg)),
                                                                      lon, lat)
            stations[station['station_id']] = {'x': x, 'y': y}
        X = [v['x'] for k, v in stations.items()]
        Y = [v['y'] for k, v in stations.items()]

        print('{:0f} x {:0f} meters'.format(max(Y) - min(Y), max(X) - min(X)))
        ax = plt.subplot(ceil(len(sysset) / 3), 3, i, aspect='equal')
        plt.scatter(X, Y, c='black', alpha=0.25)
        xmar = (20000 - (max(X) - min(X))) / 2
        ymar = (40000 - (max(Y) - min(Y))) / 2
        plt.xlim(min(X) - xmar, max(X) + xmar)
        plt.ylim(min(Y) - ymar, max(Y) + ymar)
        ax.axis('off')

#plt.axes().set_aspect('equal')
plt.show()
#plt.savefig('c:/tmp/foo.pdf')
#(min(X) - xmar, max(X) + xmar)
#(min(Y) - ymar, max(Y) + ymar)
#x = [0, 1, 2]
#y = [2, 4, 6]
#plt.scatter(x, y)
