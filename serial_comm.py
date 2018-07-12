import Adafruit_BBIO.UART as UART  # TO USE UART OF ADAFRUIT.	
import serial #FOR SERIAL COMMUNICATION SERIAL LIBRARY OF PYTHON IS INCLUDED
UART.setup("UART1")#UART1 HAS BEEN SETUP FOR SERIAL COMMUNICATION
ser= serial.Serial(port ="/dev/tty0")
ser.baudrate =9600
ser.close()
ser.open()
if ser.isOpen():
	print "Serial is open!"
	ser.write("Hello world")
ser.close()
