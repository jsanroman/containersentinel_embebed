from neo import Accel # import accelerometer
from neo import Magno # import magnometer
from neo import Gyro # import gyroscope
from neo import Temp #import libraries

import os
import time
import threading
import requests

URL_SEND = "http://fake.url/data"
HOSTNAME = "www.google.com"

TEMP_PERIOD = 10
GYRO_PERIOD = 1
MAGNO_PERIOD = 1
ACCEL_PERIOD = 0.2

DATA_FILE = "file.dat"

ACCEL_TRESHOLD = 200

gyro = Accel() # new objects p.s. this will auto initialize the device onboard
accel = Gyro()
magno = Magno()

temp = Temp() # init objects p.s. I auto initialize/reset the modules on these calls

accel.calibrate()
gyro.calibrate() # Reset current values to 0
magno.calibrate()

lock = threading.Lock()
oldAccelVals = accel.get()

def check_ping():
    response = os.system("ping -c 1 " + HOSTNAME)
    # and then check the response... True if has network
    return response == 0

def writeFile(dataType, d1, d2 = None, d3 = None):
	lock.acquire()
	ts = int(time.time() * 1000)

	with open(DATA_FILE,"a+") as f:
		line = str(ts) + ", " + dataType + ", " + str(d1)
		if d2 is not None:
			line += ", " + str(d2)
		if d3 is not None:
			line += ", " + str(d3)
		line += "\n"
		f.write(line)
	lock.release()

def sendFile():
	lock.acquire()
	with open(DATA_FILE, 'r') as myfile:
		data=myfile.read()
	r = requests.post(URL_SEND, data = {'data' : data})
	r.status_code
	lock.release()

def readTemp():
	#tempval = (temp.getTemp("f") -  32) * 5/9 # replace f with c to get celcius
	tempval = temp.getTemp("c")
	print "Current temp from sensor 1: " + str(tempval) + "\n" #need to turn into string before building strings
	writeFile("temp", tempval)
	t = threading.Timer(TEMP_PERIOD, readTemp)
	t.start()

def readGyro():
	gyroVals = gyro.get() # Returns a full xyz list [x,y,z] realtime (integers/degrees)
	print "Gyroscope X: "+str(gyroVals[0])+" Y: "+str(gyroVals[1])+" Z: "+str(gyroVals[2]) + "\n"
	writeFile("gyro", gyroVals[0], gyroVals[1], gyroVals[2])
	t = threading.Timer(GYRO_PERIOD, readGyro)
	t.start()

def readMagno():
	magnoVals = magno.get() # Above
	print "Magnometer X: "+str(magnoVals[0])+" Y: "+str(magnoVals[1])+" Z: "+str(magnoVals[2]) + "\n"
	writeFile("magno", magnoVals[0], magnoVals[1], magnoVals[2])
	t = threading.Timer(MAGNO_PERIOD, readMagno)
	t.start()

def readAccel():
	global oldAccelVals

	accelVals = accel.get() # Same as gyro return xyz of current displacment force

	#print "Accelerometer X *******: "+str(accelVals[0])+" Y: "+str(accelVals[1])+" Z: "+str(accelVals[2]) + "\n"
	#print "Accelerometer X ///////: "+str(oldAccelVals[0])+" Y: "+str(oldAccelVals[1])+" Z: "+str(oldAccelVals[2]) + "\n"

	if (abs(oldAccelVals[0] - accelVals[0]) > ACCEL_TRESHOLD) or \
			(abs(oldAccelVals[1] - accelVals[1]) > ACCEL_TRESHOLD) or \
			(abs(oldAccelVals[2] - accelVals[2]) > ACCEL_TRESHOLD):
		print "Accelerometer X: "+str(accelVals[0])+" Y: "+str(accelVals[1])+" Z: "+str(accelVals[2]) + "\n"
		writeFile("accel", accelVals[0], accelVals[1], accelVals[2])

	oldAccelVals = accelVals[:]
	t = threading.Timer(ACCEL_PERIOD, readAccel)
	t.start()

readTemp()
readGyro()
readMagno()
readAccel()








