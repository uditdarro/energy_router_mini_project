# Python program to implement client side of chat room.
import socket
import select
import sys
import os
import Adafruit_BBIO.GPIO as GPIO
import threading
import Adafruit_BBIO.UART as UART  # TO USE UART OF ADAFRUIT.   
import serial #FOR SERIAL COMMUNICATION SERIAL LIBRARY OF PYTHON IS INCLUDED


#########################This part is for initializing the GPIO later to be converted in module################################
outpin="P9_12"  #gives a name to the P9_12 pin 
GPIO.setup(outpin,GPIO.OUT) #sets the outpin to output pin
###############################################################################################################################

##########################UART INITIALIZATION ################################################################################
UART.setup('UART1')#UART1 HAS BEEN SETUP FOR SERIAL COMMUNICATION
ser= serial.Serial(port ="/dev/ttyO1",baudrate=115200,timeout =0.5)
##############################################################################################################################

##########################This part is for intializing the client and connecting it to a server################################
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print "Correct usage: script, IP address, port number"
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))
print 'server_msg'+server.recv(2048)
#############################################################################################################################

###########################This part is regarding signaling and list and tuples related to that##############################
#tup to check wether the message recived is in the command
tups_command = ('connect_req','open','close','conn_request','disconnect_req')#set of command which can be recived
tups_ack     = ('connect_ack','invalidcommand','dissconnect_ack')
tups_ser_command={'connect','disconnect'}
dic_ser_norm={'close':'connect' , 'open':'disconnect','connect':'connnect','disconnect':'disconnect'}     
dic_norm = {'connect_req': 'connect_req_ack','request_connect':'request_done','open':'open_done','close':'close_done','disconnect_req':'disconnect_req_ack'}#response to the set of command when there is no exception
############################################################################################################################

def recv(server):
 while True:
	message=server.recv(2048)
	message=message.decode('ASCII')
	message=message.strip()
	message=message.lower()
	print 'Server:'+ message
	if message in tups_command:	#to check wether the recived command is in tuple or not
		if message == 'open':
			TX(dic_ser_norm[message])
				
		elif message == 'close':
			TX(dic_ser_norm[message])
			
		else:
			server.send(dic_norm[message].encode('ASCII'))
			print(dic_norm[message])
	elif message in tups_ack:
			pass
	else:
			server.send(b'invalidcommand')
####################################################################################################################################



####################################UART RECIVER THREAD#########################################################################
def TX(command):
               # print (command)
                ser.write(command)
###################################################################################################################################


###################################UART TX THREAD ###############################################################################
def RX():
	while True:
		a = ser.read(10)
		if a in tups_ser_command:
			server.send(dic_ser_norm[a].encode('ASCII'))			
			print 'Beaglebone:'+ a
#######################################################################################################################################
#to start the reciver thread
t1=threading.Thread(target=recv,args=(server,))
t3=threading.Thread(target=RX,args=())
t1.start()
t3.start()
#this is send any command from client to the server.
while True:

            message = sys.stdin.readline()
            server.send(message)
            sys.stdout.write("<You>")
            sys.stdout.write(message)
            sys.stdout.flush()

server.close()
