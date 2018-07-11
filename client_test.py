import socket
import sys
try:
	s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print "Socket successfully created"
except  socket.error as err:
	print "creation failed with %s" %(err)

portno=80
hostname= raw_input("write the name of the site");
try:
	host_ip=socket.gethostbyname(hostname)
	print host_ip
except socket.gaierror:
	print "this was an error resolving the host"
	sys.exit()
s.connect((host_ip,portno))
print "the socket has been succesfully created to %s" %(host_ip)
message = raw_input("what you have to send")
file_open = open('DB3.cir',"r")
if file_open.mode == "r" : 
	content= file_open.read()
	print content 
while(1): s.send(message)
buff = s.recv(1024)
print "the recived message is %s" %(buff)
s.close()
