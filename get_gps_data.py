#!/usr/bin/python


import serial
import time

ser = serial.Serial('/dev/ttyUSB0',9600,timeout=1)
ser.flushOutput()

print 'Serial connected'

while True:
    r = ser.readline()
    if r.startswith("$GPRMC"):
        print "is location"
        print r
        fields = r.split(",")
        if fields[2] == "A":

            if fields[4] == "N":
                lat = float(fields[3]) / 10
            else:
                lat = -float(fields[3]) / 10

            if fields[6] == "E":
                lon = float(fields[5]) / 10
            else:
                lon = -float(fields[5]) / 10

            print str(lat) + ", " + str(lon)



