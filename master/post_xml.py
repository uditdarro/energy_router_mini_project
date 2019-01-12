# -*- coding: utf-8 -*-


import socket
import select
import sys
import threading
import os
import subprocess
import netifaces as ni   # to get a interface ip address
import random            # to produce random number for a file
import xml.dom.minidom   # used for file parsing
from collections import namedtuple #used for making structure 
import time
import errno
from socket import error as socket_error



process = subprocess.Popen("ifconfig | grep eth0 | awk '{print $1}'", shell =True, stdout =subprocess.PIPE)
try:
    outs, errs = process.communicate()
    print (outs)
except:
    process.kill()
    outs, errs = process.communicate()
    print(errs)
    sys.exit()
    
port_no = 8050
ni.ifaddresses(str(outs.strip()))
ip_addr = ni.ifaddresses(str(outs.strip()))[ni.AF_INET][0]['addr']  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip_addr,int(port_no))) ## create a server for listening poll reqeust from the server
server.listen(100)
id_no = 1024
# Set the name of the XML file.
xml_file = "try1.xml"

headers = {'Content-Type':'text/xml'}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect(("10.0.0.1",8000))
command = '<xml version="1.0" encoding="UTF-8"><header/><body><code><body/>'
command1 = 'the day was good'
with open("try1.xml","r") as f:
    data= f.read()
    s.send(data.encode('ASCII'))
    s.close()
print("Programme ends here")

# Open the XML file.
#with open(xml_file) as xml:
    # Give the object representing the XML file to requests.post.
    #r = requests.post('172.18.0.8', data=xml)

#print (r.content);

def start_conn():
    while True:
        conn, addr = server.accept()
        print("conn recived{}".format(conn))
        message = conn.recv(4096)
        if message:
               f =open("recive_file.xml","w")      ### recive_file.xml to store the message of head node
               message =message.decode('ASCII')
               f.write(message)
               f.close()
               try:
                   doc= xml.dom.minidom.parse("recive_file.xml")
               except:
                   print("The document file recived is not correct")
               #tag_name = doc.getElementsByTagName("Verb")
               verb = doc.getElementsByTagName("Verb")
               verb = verb[0].firstChild.nodeValue.encode('utf-8')
               if verb.strip() == 'poll':
                   id = doc.getElementsByTagName("id")
                   id = id[0].firstChild.nodeValue.encode('utf-8')
                   print  ("we are inside poll")
                   if int(id.strip()) == id_no:
                       print("Load ID number is same")
                       try:
                               s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                               s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                               print("socket is created")
                               s.connect(("10.0.0.1",8010)) # this corresponds to poll_read socket in receive_xml.py file
                               print("socket is connected")
                               with open("get.xml","r") as f:  ##get.xml contains poll response
                                   data= f.read()
                                   s.send(data.encode('ASCII'))
                                   s.close()
                                   print("File transfer Completed")
                       except socket_error as serr:
                           print("There is a socket error {}".format(serr))
    server.close()                       
                   
if __name__ == "__main__":
    
    t1 = threading.Thread(target =start_conn(), args=())
    t1.start()

    while True:
        pass