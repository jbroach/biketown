"""Check Biketown trips for start/end location discrepancies."""

import csv

d = {}
nt = 0
with open('c:/Data/Biketown/2018_03.csv', 'r') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r['BikeID'] not in d:
            d[r['BikeID']] = []
        d[r['BikeID']].append(r)
        nt += 1
print('Read {} records for {} bikes'.format(nt, len(d)))

tol = 0.0002

shifted_loc = set()
shifted_hub = set()
for bike in d:
    plat = None
    plon = None
    phub = None
    skip = False
    for r in d[bike]:
        try:
            slat = float(r['StartLatitude'])
            slon = float(r['StartLongitude'])
        except ValueError:
            skip = True
        if plat is not None and skip is False:
            #print('{},{} {},{} {:4f} {:4f}'.format(plat, plon, slat, slon, abs(plat - slat), abs(abs(plon) - abs(slon))))
            #input()
            if abs(plat - slat) > tol or abs(abs(plon) - abs(slon)) > tol:
                shifted_loc.add(r['RouteID'])
            if phub != r['StartHub']:
                shifted_hub.add(r['RouteID'])
        elif skip is True:
            plat = None
            plon = None
            phub = None
            skip = False
        try:
            plat = float(r['EndLatitude'])
            plon = float(r['EndLongitude'])
            phub = r['EndHub']
        except ValueError:
            pass


print('{} trip starts had location shifts of at least {} ft'
      .format(len(shifted_loc), round(tol*49*5280)))
print('{} trip starts had hub shifts'.format(len(shifted_hub)))
