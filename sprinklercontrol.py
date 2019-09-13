import json
import urllib.error
from urllib.request import urlopen
from datetime import datetime
from time import time

class valve:
    def __init__(self, name, area):
        self.name = name
        self.area = area #area of yard covered
        self.runtimes = list()
        self.open = False
        self.override = False
        
    def append_timetable(self, date, starttime, endtime):
        k = 0
        while k in self.runtimes:
            k += 1
        self.runtimes.append({}) #append empty dict
        self.runtimes[k]['startdate'] = date
        self.runtimes[k]['starttime'] = starttime
        self.runtimes[k]['endtime'] = endtime
        
    def open_valve(self):
        self.open = True
        print("opened {}".format(self.name))
        
    def close_valve(self):
        self.open = False
        print("closed {}".format(self.name))

with open("key.txt", 'r') as k:
    key = k.read().strip()

with open("config.txt", 'r') as c:
    conf = c.read().splitlines()
    lat = conf[0]
    long = conf[1]
    updateinterval = int(conf[2]) #in seconds
    pthreshold = float(conf[3]) #rain chance needed to override
    
with open("timetable.json", 'r') as j:
    timedata = json.load(j)

v = list() #list of all valve classes
n = 0
for entry in timedata['valves']: #create all valve classes from .json file
    v.append(valve(entry['name'], entry['area']))
    for runtime in entry['runtimes']:
        stime = datetime.strptime(runtime['starttime'], '%I:%M%p') 
        etime = datetime.strptime(runtime['endtime'], '%I:%M%p')
        if etime < stime:
            print("Warning: starttime occurs after endtime for {} - skipping entry".format(v[n].name))
        else:
            v[n].append_timetable(runtime['startdate'], runtime['starttime'], runtime['endtime'])
    n += 1

wapi = "https://api.darksky.net/forecast/{}/{},{}".format(key, lat, long)
lastapicall = 0
precip = 0

while 1:
    current = str(datetime.fromtimestamp(time()).strftime('%I:%M%p'))

    if int(time()) - int(lastapicall) > updateinterval: 
        print(current)
        try:
            data = json.loads(urlopen(wapi).read())
            precip = data["currently"]["precipProbability"]
        except urllib.error.URLError:
            print("Error occured trying to connect to weather API")
        lastapicall = time()
        print(precip)
        
    for entry in v:
        for runtime in entry.runtimes:
            if int(datetime.today().weekday()) in runtime['startdate']:
                if runtime['starttime'] == current and entry.open == False and entry.override == False:
                    if precip <= pthreshold:
                        entry.open_valve()
                    else:
                        print("Precipitation probability exceeds threshold, override {}".format(entry.name))
                        entry.override = True
                elif runtime['endtime'] == current and entry.open == True: 
                    entry.close_valve()
                elif runtime['endtime'] == current and entry.override == True: 
                    entry.override = False #reset override after intended cycle is over