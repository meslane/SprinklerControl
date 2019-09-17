import json
import urllib.error
from urllib.request import urlopen
from datetime import datetime
from time import time
from time import sleep

class valve:
    def __init__(self, name, area):
        self.name = name
        self.area = area
        self.runtimes = list()
        self.open = False
        self.override = False
        
    def append_timetable(self, date, starttime, endtime):
        k = 0
        while k in self.runtimes:
            k += 1
        self.runtimes.append({})
        self.runtimes[k]['startdate'] = date
        self.runtimes[k]['starttime'] = starttime
        self.runtimes[k]['endtime'] = endtime
        
    def open_valve(self):
        #TODO: put GPIO code
        self.open = True
        print("opened {}".format(self.name))
        
    def close_valve(self):
        #TODO: put GPIO code
        self.open = False
        sleep(0.05) #sleep for 50ms to let the coil fully release
        print("closed {}".format(self.name))

with open("key.txt", 'r') as k:
    key = k.read().strip()
    
with open("timetable.json", 'r') as j:
    timedata = json.load(j)

v = list()
n = 0
for entry in timedata['valves']: #create all valve classes from .json file
    v.append(valve(entry['name'], entry['area']))
    for runtime in entry['runtimes']:
        if datetime.strptime(runtime['endtime'], '%I:%M%p') < datetime.strptime(runtime['starttime'], '%I:%M%p'):
            print("Warning: starttime occurs after endtime for {} - skipping entry".format(v[n].name))
        else:
            v[n].append_timetable(runtime['startdate'], runtime['starttime'], runtime['endtime'])
    n += 1

wapi = "https://api.darksky.net/forecast/{}/{},{}".format(key, timedata['lat'], timedata['long'])
lastapicall = 0
precip = 0
while 1:
    current = str(datetime.fromtimestamp(time()).strftime('%I:%M%p'))

    if int(time()) - int(lastapicall) > timedata['APIUpdateInterval']: 
        print(current)
        try:
            data = json.loads(urlopen(wapi).read())
            precip = data['currently']['precipProbability']
        except urllib.error.URLError:
            print("Error occured trying to connect to weather API")
        lastapicall = time()
        print(precip)
        
    for entry in v:
        for runtime in entry.runtimes:
            if int(datetime.today().weekday()) in runtime['startdate']:
                if runtime['endtime'] == current and entry.open == True: 
                    entry.close_valve()
                elif runtime['endtime'] == current and entry.override == True: 
                    entry.override = False #reset override after intended cycle is over
                elif runtime['starttime'] == current and entry.open == False and entry.override == False:
                    if precip <= timedata['precipThreshold']:
                        entry.open_valve()
                    else:
                        print("Precipitation probability exceeds threshold, override {}".format(entry.name))
                        entry.override = True