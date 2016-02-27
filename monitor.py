from neo import Accel # import accelerometer
from neo import Magno # import magnometer
from neo import Gyro # import gyroscope
from neo import Temp #import libraries

import time

ACCEL_TRESHOLD = 1000

gyro = Accel() # new objects p.s. this will auto initialize the device onboard
accel = Gyro()
magno = Magno()

temp = Temp() # init objects p.s. I auto initialize/reset the modules on these calls

accel.calibrate()
gyro.calibrate() # Reset current values to 0
magno.calibrate()

def writeFile(ts, dataType, d1, d2 = None, d3 = None):
	with open("file.dat","a+") as f:
		line = str(ts) + ", " + dataType + ", " + str(d1)
		if d2 is not None:
			line += ", " + str(d2)
		if d3 is not None:
			line += ", " + str(d3)
		line += "\n"
		f.write(line)

oldAccelVals = accel.get()

while True: # Run forever
	ts = int(time.time() * 1000)

	tempVal = (temp.getTemp("f") -  32) * 5/9 # replace f with c to get celcius
	print "Current temp from sensor 1: "+str(tempVal) #need to turn into string before building strings

	gyroVals = gyro.get() # Returns a full xyz list [x,y,z] realtime (integers/degrees)
	print "Gyroscope X: "+str(gyroVals[0])+" Y: "+str(gyroVals[1])+" Z: "+str(gyroVals[2])# turn current values (ints) to strings
	writeFile(ts, "gyro", gyroVals[0], gyroVals[1], gyroVals[2])

	accelVals = accel.get() # Same as gyro return xyz of current displacment force
	print "Accelerometer X: "+str(accelVals[0])+" Y: "+str(accelVals[1])+" Z: "+str(accelVals[2])

	if abs(oldAccelVals[0] - accelVals[0]) > ACCEL_TRESHOLD or \
		abs(oldAccelVals[1] - accelVals[1]) > ACCEL_TRESHOLD or \
		abs(oldAccelVals[2] - accelVals[2]) > ACCEL_TRESHOLD:
		writeFile(ts, "accel", accelVals[0], accelVals[1], accelVals[2])

	oldAccelVals = accelVals

	magnoVals = magno.get() # Above
	print "Magnometer X: "+str(magnoVals[0])+" Y: "+str(magnoVals[1])+" Z: "+str(magnoVals[2])
	writeFile(ts, "magno", magnoVals[0], magnoVals[1], magnoVals[2])

	print "" # newline
	time.sleep(1) # wait a second






