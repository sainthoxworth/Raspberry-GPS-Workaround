from gps import *
import time
import firebase_admin
from firebase_admin import db
from datetime import datetime


cred_obj = firebase_admin.credentials.Certificate('key.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': 'https://ytu-surucu-destek-sistemi-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference("/")

rasp_key = ref.child('raspberry')

running = True

def getPositionData(gps):
    nx = next(gpsd)
    if nx['class'] == 'TPV':
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        latitude = getattr(nx, 'lat', "Unknown")
        longitude = getattr(nx, 'lon', "Unknown")
        rasp_key.update(
            {
                'latitude': latitude,
                'longitude': longitude,
                'time': current_time
        })
        print(("Konumunuz: lon = " + str(longitude) + ", lat = " + str(latitude)))


gpsd = gps(mode = WATCH_ENABLE | WATCH_NEWSTYLE)

try:
    print("Uygulama calisiyor!")
    while running:
        getPositionData(gpsd)
        time.sleep(1.0)

except(KeyboardInterrupt):
    running = False
    print("Uygulama kapandi!")