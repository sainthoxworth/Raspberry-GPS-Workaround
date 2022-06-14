from gps import *
import time
import firebase_admin
from firebase_admin import db
from datetime import datetime
import RPi.GPIO as GPIO
import time
import cv2
import  pyshine

HTML="""
<html>
<head>
<title>PyShine Live Streaming</title>
</head>

<body>
<center><h1> PyShine Live Streaming using OpenCV </h1></center>
<center><img src="stream.mjpg" width='640' height='480' autoplay playsinline></center>
</body>
</html>
"""

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
    
    rightWarning = distance1 > 10 
    leftWarning = distance > 10
    
    ## distance1 is right, distance is left
    

    if nx['class'] == 'TPV':
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
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
                'leftWarning': str(leftWarning),
                'rightWarning': str(rightWarning),
                
        })
        print(("Konumunuz: lon = " + str(longitude) + ", lat = " + str(latitude)
               + "Zaman: " + str(current_time)
               + "Hız: " + str(speed))
               + " Uzaklık: " + str(distance))


def picam():
    StreamProps = ps.StreamProps
    StreamProps.set_Page(StreamProps,HTML)
    address = ('192.168.1.1',9000) # Enter your IP address 
    try:
        StreamProps.set_Mode(StreamProps,'cv2')
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_BUFFERSIZE,4)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH,320)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
        capture.set(cv2.CAP_PROP_FPS,30)
        StreamProps.set_Capture(StreamProps,capture)
        StreamProps.set_Quality(StreamProps,90)
        server = ps.Streamer(address,StreamProps)
        print('Server started at','http://'+address[0]+':'+str(address[1]))
        server.serve_forever()
        
    except KeyboardInterrupt:
        capture.release()
        server.socket.close()

gpsd = gps(mode = WATCH_ENABLE | WATCH_NEWSTYLE)

try:
    print("Uygulama calisiyor!")
    while running:
        getPositionData(gpsd)
        time.sleep(1.0)
        picam()

except(KeyboardInterrupt):
    running = False
    print("Uygulama kapandi!")