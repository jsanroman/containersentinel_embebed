#!/usr/bin/python

from neo import Accel
from neo import Magno
from neo import Gyro
from neo import Temp

import os
import time
import threading
import requests
import ConfigParser
import json
import serial
import time

config = ConfigParser.RawConfigParser()
config.read(r'monitor.cfg')

DEVICE_ID = config.get('monitor', 'device_id')
TEMP_PERIOD = config.getfloat('monitor', 'temp_period')
GYRO_PERIOD = config.getfloat('monitor', 'gyro_period')
MAGNO_PERIOD = config.getfloat('monitor', 'magno_period')
ACCEL_PERIOD = config.getfloat('monitor', 'accel_period')
ACCEL_TRESHOLD = config.getfloat('monitor', 'accel_treshold')
GPS_PERIOD = config.getfloat('monitor', 'gps_period')
SEND_FILE_PERIOD = config.getfloat('monitor', 'send_file_period')
DATA_FILE = config.get('monitor', 'data_file')
URL_SEND = config.get('monitor', 'endpoint')

gyro = Accel() # new objects p.s. this will auto initialize the device onboard
accel = Gyro()
magno = Magno()
temp = Temp()

 # Reset current values to 0
accel.calibrate()
gyro.calibrate()
magno.calibrate()

lock = threading.Lock()
oldAccelVals = accel.get()

ser = serial.Serial('/dev/ttyUSB0',9600,timeout=1)
ser.flushOutput()

def getLocation():
	try:
		r = requests.get("http://freegeoip.net/json/")
		print "Status code = " +  str(r.status_code)

		if r.status_code != 200:
			return None
		d = json.loads(r.content)
		return [d['latitude'], d['longitude']]
	except Exception as e:
		print e
		return None

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
	print "++++++++++++++++++++++++++++ Sending file..."
	# coords = getLocation()
	# if coords == None:
	# 	print '++++++++++++++++++++++++++++ No network connection'
	# else:
	#	writeFile("gps", coords[0], coords[1])

	lock.acquire()
	try:
		with open(DATA_FILE, 'r') as myfile:
			data = myfile.read()
		r = requests.post(URL_SEND, data={'device_id': DEVICE_ID, 'data': data})
		print "++++++++++++++++++++++++++++ HTTP status code = " + str(r.status_code)
		if r.status_code == 200 or r.status_code == 204:
			os.remove(DATA_FILE)
		print "++++++++++++++++++++++++++++ File sent"
	except:
		pass
	lock.release()
	t = threading.Timer(SEND_FILE_PERIOD, sendFile)
	t.start()

def readTemp():
	#tempval = (temp.getTemp("f") -  32) * 5/9 # replace f with c to get celcius
	tempval = temp.getTemp("c")
	print "Temperature: " + str(tempval) #need to turn into string before building strings
	writeFile("temp", tempval)
	t = threading.Timer(TEMP_PERIOD, readTemp)
	t.start()

def readGyro():
	gyroVals = gyro.get() # Returns a full xyz list [x,y,z] realtime (integers/degrees)
	print "Gyroscope X: "+str(gyroVals[0])+" Y: "+str(gyroVals[1])+" Z: "+str(gyroVals[2])
	writeFile("gyro", gyroVals[0], gyroVals[1], gyroVals[2])
	t = threading.Timer(GYRO_PERIOD, readGyro)
	t.start()

def readMagno():
	magnoVals = magno.get() # Above
	print "Magnometer X: "+str(magnoVals[0])+" Y: "+str(magnoVals[1])+" Z: "+str(magnoVals[2])
	writeFile("magno", magnoVals[0], magnoVals[1], magnoVals[2])
	t = threading.Timer(MAGNO_PERIOD, readMagno)
	t.start()

def readAccel():
	global oldAccelVals
	accelVals = accel.get() # Same as gyro return xyz of current displacement force

	if (abs(oldAccelVals[0] - accelVals[0]) > ACCEL_TRESHOLD) or \
			(abs(oldAccelVals[1] - accelVals[1]) > ACCEL_TRESHOLD) or \
			(abs(oldAccelVals[2] - accelVals[2]) > ACCEL_TRESHOLD):
		print "Accelerometer X: "+str(accelVals[0])+" Y: "+str(accelVals[1])+" Z: "+str(accelVals[2])
		writeFile("accel", accelVals[0], accelVals[1], accelVals[2])

	oldAccelVals = accelVals[:]
	t = threading.Timer(ACCEL_PERIOD, readAccel)
	t.start()

def readGps():
	print "Search for location"
	while True:
		r = ser.readline()
		if r.startswith("$GPRMC"):
			print r
			fields = r.split(",")
			if fields[2] == "A":
				if fields[4] == "N":
					lat = float(fields[3]) / 100
				else:
					lat = -float(fields[3]) / 100
				if fields[6] == "E":
					lon = float(fields[5]) / 100
				else:
					lon = -float(fields[5]) / 100
				print str(lat) + ", " + str(lon)
				writeFile("gps", lat, lon)
			else:
				break
	t = threading.Timer(GPS_PERIOD, readGps)
	t.start()

readTemp()
readGyro()
readMagno()
readAccel()
readGps()
sendFile()








