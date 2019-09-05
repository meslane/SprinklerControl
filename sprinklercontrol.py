import urllib.error
from urllib.request import urlopen
import json
from datetime import datetime
from time import time

class valve:
    def __init__(self, name, area):
        self.name = name #valve 1-6
        self.area = area #area of yard covered
        self.open = False
        
    def open(self):
        self.open = True
        
    def close(self):
        self.open = False

with open("key.txt", 'r') as k:
    key = k.read().strip()

with open("config.txt", 'r') as c:
    conf = c.read().splitlines()
    lat = conf[0]
    long = conf[1]
    updateinterval = conf[2] #in seconds

wapi = "https://api.darksky.net/forecast/{}/{},{}".format(key, lat, long)

lastapicall = 0
precip = 0

while 1:
    current = time()

    if int(current) - int(lastapicall) > int(updateinterval): 
        try:
            data = json.loads(urlopen(wapi).read())
            precip = data["currently"]["precipProbability"]
        except urllib.error.URLError:
            print("Error occured trying to connect to weather API")
        lastapicall = time()
        print(precip)
        print(time())