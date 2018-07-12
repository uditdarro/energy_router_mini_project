import Adafruit_BBIO.GPIO as GPIO #TYPE THE Adafruit library name correclty. Library is used for using GPIO
outPin="P9_12" #WRITE THE P9_12 CORRECTLY IT DEFINES THE PIN NUMBER WHICH YOU WANT TO USE AND GIVE IT A NAME
GPIO.setup(outPin,GPIO.OUT) #SET IT OUT AS A OUT PIN	
from time import sleep #IMPORT SLEEP FROM TIME LIBRARY TO USE IT AS A DELAY
for i in range(0,5):
	GPIO.output(outPin,GPIO.HIGH)
	sleep(3)
	GPIO.output(outPin,GPIO.LOW)
	sleep(3)
GPIO.cleanup()# THIS COMMAND RELEASE THE GPIO RESOURCE
