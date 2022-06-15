from gps import *
import time
import firebase_admin
from firebase_admin import db
from datetime import datetime
import RPi.GPIO as GPIO
import time

cred_obj = firebase_admin.credentials.Certificate('key.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': 'https://ytu-surucu-destek-sistemi-default-rtdb.europe-west1.firebasedatabase.app/'
})

GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24

print ("Mesafe olculuyor...")

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

ref = db.reference("/")

rasp_key = ref.child('users/TX3SudStPQSDPViRvZ9kaOlmw4H2')

running = True

def getPositionData(gps):
    GPIO.setwarnings(False)
    nx = next(gpsd)
    GPIO.output(TRIG, False)

    print("Sensor 1 bekleniyor...")
    time.sleep(2)
    

    GPIO.output(TRIG, True)
    time.sleep(0.00001)

    GPIO.output(TRIG, False)
    

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
 
    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150
    distance = round(distance, 2)
    
    ######################### SAĞ SENSÖR ############################
    
    GPIO.setmode(GPIO.BCM)
    TRIG1 = 20
    ECHO1 = 21

    GPIO.setup(TRIG1, GPIO.OUT)
    GPIO.setup(ECHO1, GPIO.IN)

    GPIO.output(TRIG1, False)

    print("Sensor 2 bekleniyor...")
    time.sleep(2)

    GPIO.output(TRIG1, True)
    time.sleep(0.00001)

    GPIO.output(TRIG1, False)
	
    while GPIO.input(ECHO1) == 0:
        pulse_start1 = time.time()

    while GPIO.input(ECHO1) == 1:
        pulse_end1 = time.time()

    pulse_duration1 = pulse_end1 - pulse_start1

    distance1 = pulse_duration1 * 17150
    distance1 = round(distance1, 2)
    
    ######################### ÖN SENSÖR ############################
    
    GPIO.setmode(GPIO.BCM)
    TRIG2 = 8
    ECHO2 = 7

    GPIO.setup(TRIG2, GPIO.OUT)
    GPIO.setup(ECHO2, GPIO.IN)

    GPIO.output(TRIG2, False)

    print("Sensor 3 bekleniyor...")
    time.sleep(2)

    GPIO.output(TRIG2, True)
    time.sleep(0.00001)

    GPIO.output(TRIG2, False)
	
    while GPIO.input(ECHO2) == 0:
        pulse_start2 = time.time()

    while GPIO.input(ECHO2) == 1:
        pulse_end2 = time.time()

    pulse_duration2 = pulse_end2 - pulse_start2

    distance2 = pulse_duration2 * 17150
    distance2 = round(distance2, 2)
    
    
    ######################### SENSÖRLERİN BOOLEAN UYARI DEĞERLERİ ############################

    frontWarning = distance2 < 10
    rightWarning = distance1 < 10 
    leftWarning = distance < 10
    
    ## distance 2 is front, distance1 is right, distance is left
    

    if nx['class'] == 'TPV':
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        latitude = getattr(nx, 'lat', "Bilinmeyen veri")
        # $GPRMC,123519,A, 4807.038,N, 01131.000,E, 022.4, 084.4,230394,003.1,W*6A
        longitude = getattr(nx, 'lon', "Bilinmeyen veri")
        speed = getattr(nx, 'speed', "Bilinmeyen veri")
        rasp_key.update(
            {
                'latitude': str(latitude),
                'longitude': str(longitude),
                'gpsSpeed': str(speed),
                'time': str(current_time),
                'leftDistance': str(distance),
                'rightDistance': str(distance1),
                'frontDistance': str(distance2),
                'leftWarning': str(leftWarning),
                'rightWarning': str(rightWarning),
                'frontWarning': str(frontWarning)
                
        })
        print(("Konumunuz: lon = " + str(longitude) + ", lat = " + str(latitude)
               + "Zaman: " + str(current_time)
               + "Hız: " + str(speed))
               + "Sol Uzaklık: " + str(distance))
               + "Sağ Uzaklık: " + str(distance1))
               + "Ön Uzaklık: " + str(distance2))


gpsd = gps(mode = WATCH_ENABLE | WATCH_NEWSTYLE)

try:
    print("Uygulama calisiyor!")
    while running:
        getPositionData(gpsd)
        time.sleep(1.0)

except(KeyboardInterrupt):
    running = False
    print("Uygulama kapandi!")