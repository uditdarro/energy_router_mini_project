# -*- coding: utf-8 -*-

import socket
import select
import sys
import threading
import os
import netifaces as ni   # to get a interface ip address
import random            # to produce random number for a file
import xml.dom.minidom   # used for file parsing
from collections import namedtuple #used for making structure 
import time
import errno
from socket import error as socket_error
import xml_write
import subprocess
import telnet
import net_tools as network
process = subprocess.Popen("ifconfig | grep enp2s0 | awk '{print $1}'", shell =True, stdout =subprocess.PIPE)
try:
    outs, errs = process.communicate()
    print (outs)
except:
    process.kill()
    outs, errs = process.communicate()
    print(errs)
    sys.exit()
ni.ifaddresses(outs.strip())
try:
    IPAddr = ni.ifaddresses(outs.strip())[ni.AF_INET][0]['addr']
except:
    print("Interface doesnot have a  ip address")
    
ip  =IPAddr
print("Your Computer IP Address is:" + IPAddr)    
port_no = 8000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip,int(port_no)))
server.listen(100)
#sock_poll = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
poll_portno =8050       # port number for which it will sending poll request to load
pollread_portno =8010  # port number for which poll file will be received by the server
poll_read = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
poll_read.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
poll_read.bind((ip,int(pollread_portno)))
poll_read.listen(1)
list_of_clients=[]
list_addr = []   #maintains the list of all the address connected to it
list_of_threads = []
Load_list = []   #maintains the list of all the loads connected to it
Source_list=[]  #maintains the list of  all the sources connected to it
Load_struct   =  namedtuple("Load_struct" , "ip_address id type value min_volt max_volt min_curr max_curr") #  structure  maintains all the data regarding the load
Source_struct =  namedtuple("Source_struct", "ip_address id type value min_volt max_volt min curr max_curr")# Structure maintains all the data regarding the source
def start_conn():
  while True:
 
    """Accepts a connection request and stores two parameters, 
    conn which is a socket object for that user, and addr 
    which contains the IP address of the client that just 
    connected"""
    conn, addr = server.accept()
 
    """Maintains a list of clients for ease of broadcasting
    a message to all available people in the chatroom"""
    if conn in list_of_clients:
        pass
    else:
        list_of_clients.append(conn)  # maintains the list of clients connected to it
        print(list_of_clients)
        # prints the address of the user that just connected
        print (addr[0] + " connected")
        # creates and individual thread for every user 
        # that connects
        t1=threading.Thread(target=clientthread,args=(conn,addr,)) 
        list_of_threads.append(t1)
        print(list_of_threads)
        t1.start()

def Poll():
    
    ### Poll  all the sources and loads connected to it and get there updated files ###
    """
    First check the load list get the all the updated files of the  load and then get the updated files of the sources.
    
    
    """
    while True:
        if  not Load_list:
            pass
        else:
            for i in Load_list:
                try:
                    sock_poll = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_poll.connect((i.ip_address , poll_portno))
                    xml_write.create_xml_file(i.id,'poll.xml')
                    print("sock_poll created")
                    with open("poll.xml","r") as f:  ## to send poll file to the loads/source
                        data= f.read()
                        sock_poll.send(data.encode('ASCII'))
                        sock_poll.close()
                        print("Poll file send")
                except socket_error as serr:
                        print(serr)
                        print ("Load is no more connected to the poll file")
                        del Load_list[Load_list.index(i)]
                        break
                conn , addr = poll_read.accept()
                time.sleep(3)
                message = conn.recv(4096)
                if message:
                    print("got a  poll response")
                    f =open("poll_response.xml","w")
                    message =message.decode('ASCII')
                    f.write(message)
                    f.close()
                    print("Completed writing poll response")
                    #print ("<" + addr[0] + "> " + message )
                    ##if the file is not in correct format 
                    try:
                        doc= xml.dom.minidom.parse("poll_response.xml")
                    except:
                        print("The document file recived is not correct")
                        sys.exit()
                    tag_name = doc.getElementsByTagName("Verb")
                    tag_name = tag_name[0].firstChild.nodeValue.encode('utf-8')
                    if tag_name.strip() == 'poll':
                            print("It is update response")
                            noun = doc.getElementsByTagName("Noun")
                            noun = noun[0].firstChild.nodeValue.encode('utf-8')
                            if noun.strip() == 'Load':
                                id_load     = doc.getElementsByTagName("id")
                                id_load     = id_load[0].firstChild.nodeValue.encode('utf-8')
                                id_load     = id_load.strip()
                                type_load   = doc.getElementsByTagName("type")
                                type_load   = type_load[0].firstChild.nodeValue.encode('utf-8')
                                type_load   = type_load.strip()
                                value_load  = doc.getElementsByTagName("value")
                                value_load  = value_load[0].firstChild.nodeValue.encode('utf-8')
                                value_load  = value_load.strip()
                                try:
                                    min_volt_load    = doc.getElementByTagName("Min_Voltage")
                                    min_volt_load = min_volt_load[0].firstChild.nodeValue.encode('utf-8')
                                    min_volt_load = min_volt_load.strip()
                                except:
                                    min_volt_load = None
                                try:
                                    max_volt_load    = doc.getElementsByTagName("Max_Voltage")
                                    max_volt_load = max_volt_load[0].firstChild.nodeValue.encode('utf-8')
                                    max_volt_load = max_volt_load.strip()
                                except:
                                    max_volt_load = None
                                try:
                                    min_current_load  = doc.getElementsByTagName("Min_Current")
                                    min_current_load = min_current_load[0].firstChild.nodeValue.encode('utf-8')
                                    min_current_load = min_current_load.strip()
                                except:
                                    min_current_load = None
                                try:
                                    max_current_load  =doc.getElementsByTagName("Max_Current")
                                    max_current_load = max_current_load[0].firstChild.nodeValue.encode('utf-8')
                                    max_current_load = max_current_load.strip()
                                except:
                                    max_current_load = None
                                print("||##################################||###############################||")
                                print("                                  Updated load                         ")
                                print("  ipaddress                         || {}                             ".format(addr[0]))
                                print("  Load ID                           || {}                             ".format(id_load))
                                print("  Type                              || {}                             ".format(type_load))
                                print("  Load Value                        || {}                             ".format(value_load))
                                print("  Minimum Voltage                   || {}                             ".format(min_volt_load))
                                print("  Maximum Voltage                   || {}                             ".format(max_volt_load))
                                print("  Minimum Current                   || {}                             ".format(min_current_load))
                                print("  Maximum Current                   || {}                             ".format(max_current_load))
                                print("||##################################||###############################||")
                                Load_list[Load_list.index(i)] = Load_struct(ip_address = addr[0] , id = id_load , type =type_load, value =value_load, min_volt = min_volt_load , max_volt = min_volt_load , min_curr = min_current_load, max_curr =min_current_load)
                                os.remove("poll_response.xml")
            for i in Source_list:
                try:
                    sock_poll = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_poll.connect((i.ip_address , poll_portno))
                    xml_write.create_xml_file(i.id,'poll.xml')
                    print("sock_poll created")
                    with open("poll.xml","r") as f:  ## to send poll file to the loads/source
                        data= f.read()
                        sock_poll.send(data.encode('ASCII'))
                        sock_poll.close()
                        print("Poll file send")
                except socket_error as serr:
                        print(serr)
                        print ("Load is no more connected to the poll file")
                        del Load_list[Load_list.index(i)]
                        break
                conn , addr = poll_read.accept()
                time.sleep(3)
                message = conn.recv(4096)
                if message:
                    print("got a  poll response")
                    f =open("poll_response.xml","w")
                    message =message.decode('ASCII')
                    f.write(message)
                    f.close()
                    print("Completed writing poll response")
                    #print ("<" + addr[0] + "> " + message )
                    ##if the file is not in correct format 
                    try:
                        doc= xml.dom.minidom.parse("poll_response.xml")
                    except:
                        print("The document file recived is not correct")
                        sys.exit()
                    tag_name = doc.getElementsByTagName("Verb")
                    tag_name = tag_name[0].firstChild.nodeValue.encode('utf-8')
                    if tag_name.strip() == 'poll':
                            print("It is update response")
                            noun = doc.getElementsByTagName("Noun")
                            noun = noun[0].firstChild.nodeValue.encode('utf-8')
                            if noun.strip() == 'Source':
                                id_source     = doc.getElementsByTagName("id")
                                id_source     = id_source[0].firstChild.nodeValue.encode('utf-8')
                                id_source     = id_source.strip()
                                type_source   = doc.getElementsByTagName("type")
                                type_source   = type_source[0].firstChild.nodeValue.encode('utf-8')
                                type_source   = type_source.strip()
                                value_source  = doc.getElementsByTagName("value")
                                value_source  = value_source[0].firstChild.nodeValue.encode('utf-8')
                                value_source  = value_source.strip()
                                try:
                                    min_volt_source    = doc.getElementByTagName("Min_Voltage")
                                    min_volt_source = min_volt_source[0].firstChild.nodeValue.encode('utf-8')
                                    min_volt_source = min_volt_source.strip()
                                except:
                                    min_volt_source = None
                                try:
                                    max_volt_source    = doc.getElementsByTagName("Max_Voltage")
                                    max_volt_source = max_volt_source[0].firstChild.nodeValue.encode('utf-8')
                                    max_volt_source = max_volt_source.strip()
                                except:
                                    max_volt_source = None
                                try:
                                    min_current_source  = doc.getElementsByTagName("Min_Current")
                                    min_current_source = min_current_source[0].firstChild.nodeValue.encode('utf-8')
                                    min_current_source = min_current_source.strip()
                                except:
                                    min_current_source = None
                                try:
                                    max_current_source  =doc.getElementsByTagName("Max_Current")
                                    max_current_source = max_current_source[0].firstChild.nodeValue.encode('utf-8')
                                    max_current_source = max_current_source.strip()
                                except:
                                    max_current_source = None
                                print("||##################################||###############################||")
                                print("                                 New Source joined                       ")
                                print("  ipaddress                         || {}                             ".format(addr[0]))
                                print("  Source ID                         || {}                             ".format(id_source))
                                print("  Type                              || {}                             ".format(type_source))
                                print("  Source Value                      || {}                             ".format(value_source))
                                print("  Minimum Voltage                   || {}                             ".format(min_volt_source))
                                print("  Maximum Voltage                   || {}                             ".format(max_volt_source))
                                print("  Minimum Current                   || {}                             ".format(min_current_source))
                                print("  Maximum Current                   || {}                             ".format(max_current_source))
                                print("||##################################||###############################||")
                                Source_list[Source_list.index(i)] = Source_struct(ip_address = addr[0] , id = id_load , type =type_load, value =value_load,min_volt = min_volt_source , max_volt = min_volt_source , min_curr = min_current_source, max_curr =min_current_source)
                                os.remove("poll_response.xml")
                else:
                    print("Nothing in message")
                    

def clientthread(conn, addr):
 
    # sends a message to the client whose user object is conn
     
     conn.send(b"Welcome to this chatroom!")
     message = conn.recv(4096)
     s= 'receive'
     i= str(random.randint(1,101))   
     xml_1='.xml'
     receive_xml = s+i+xml_1
     print(receive_xml)
     while True:
		#print(threading.current_thread().name)
           
           
           if message:
               f =open(receive_xml,"w")
               message =message.decode('ASCII')
               f.write(message)
               f.close()
               print ("<" + addr[0] + "> " + message )
               ##if the file is not in correct format 
               try:
                   doc= xml.dom.minidom.parse(receive_xml)
               except:
                   print("The document file recived is not correct")
                   sys.exit()
               print(doc.nodeName)
               print(doc.firstChild.tagName)
               #get the list of html tag from document and print each one
               tag_name = doc.getElementsByTagName("Verb")
               tag_name =tag_name[0].firstChild.nodeValue.encode('utf-8')
               #print(type(tag_name))
               print(tag_name)
               #post information about the port
               if tag_name.strip() == 'post':
                   print("It is  a post response")
                   verb = doc.getElementsByTagName("Noun")
                   verb = verb[0].firstChild.nodeValue.encode('utf-8')
                   if verb.strip() == 'Load':
                       ### to get the element value of the load
                       id_load     = doc.getElementsByTagName("id")
                       id_load     = id_load[0].firstChild.nodeValue.encode('utf-8')
                       id_load     = id_load.strip()
                       type_load   = doc.getElementsByTagName("type")
                       type_load   = type_load[0].firstChild.nodeValue.encode('utf-8')
                       type_load   = type_load.strip()
                       value_load  = doc.getElementsByTagName("value")
                       value_load  = value_load[0].firstChild.nodeValue.encode('utf-8')
                       value_load  = value_load.strip()
                       try:
                           min_volt_load    = doc.getElementByTagName("Min_Voltage")
                           min_volt_load = min_volt_load[0].firstChild.nodeValue.encode('utf-8')
                           min_volt_load = min_volt_load.strip()
                       except:
                           min_volt_load = None
                       try:
                           max_volt_load    = doc.getElementsByTagName("Max_Voltage")
                           max_volt_load = max_volt_load[0].firstChild.nodeValue.encode('utf-8')
                           max_volt_load = max_volt_load.strip()
                       except:
                           max_volt_load = None
                       try:
                           min_current_load  = doc.getElementsByTagName("Min_Current")
                           min_current_load = min_current_load[0].firstChild.nodeValue.encode('utf-8')
                           min_current_load = min_current_load.strip()
                       except:
                           min_current_load = None
                       try:
                           max_current_load  =doc.getElementsByTagName("Max_Current")
                           max_current_load = max_current_load[0].firstChild.nodeValue.encode('utf-8')
                           max_current_load = max_current_load.strip()
                       except:
                           max_current_load = None
                       print("||##################################||###############################||")
                       print("                                 New Load joined                       ")
                       print("  ipaddress                         || {}                             ".format(addr[0]))
                       print("  Load ID                           || {}                             ".format(id_load))
                       print("  Type                              || {}                             ".format(type_load))
                       print("  Load Value                        || {}                             ".format(value_load))
                       print("  Minimum Voltage                   || {}                             ".format(min_volt_load))
                       print("  Maximum Voltage                   || {}                             ".format(max_volt_load))
                       print("  Minimum Current                   || {}                             ".format(min_current_load))
                       print("  Maximum Current                   || {}                             ".format(max_current_load))
                       print("||##################################||###############################||")
                       load = Load_struct(ip_address = addr[0] , id = id_load , type =type_load, value =value_load , min_volt = min_volt_load , max_volt = min_volt_load , min_curr = min_current_load, max_curr =min_current_load)
                       Load_list.append(load)
                       #print(Load_list)
                       #print("print load structure{}" .format(load))
                       #print("print laod structue value{}" .format(Load_list[0].value))
                   else:
                       pass
                   if verb.strip() == 'Source':
                       ### to get the element value of the load
                       id_source     = doc.getElementsByTagName("id")
                       id_source     = id_source[0].firstChild.nodeValue.encode('utf-8')
                       id_source     = id_source.strip()
                       type_source   = doc.getElementsByTagName("type")
                       type_source   = type_source[0].firstChild.nodeValue.encode('utf-8')
                       type_source   = type_source.strip()
                       value_source  = doc.getElementsByTagName("value")
                       value_source  = value_source[0].firstChild.nodeValue.encode('utf-8')
                       value_source  = value_source.strip()
                       try:
                           min_volt_source    = doc.getElementByTagName("Min_Voltage")
                           min_volt_source = min_volt_source[0].firstChild.nodeValue.encode('utf-8')
                           min_volt_source = min_volt_source.strip()
                       except:
                           min_volt_source = None
                       try:
                           max_volt_source    = doc.getElementsByTagName("Max_Voltage")
                           max_volt_source = max_volt_source[0].firstChild.nodeValue.encode('utf-8')
                           max_volt_source = max_volt_source.strip()
                       except:
                           max_volt_source = None
                       try:
                           min_current_source  = doc.getElementsByTagName("Min_Current")
                           min_current_source = min_current_source[0].firstChild.nodeValue.encode('utf-8')
                           min_current_source = min_current_source.strip()
                       except:
                           min_current_source = None
                       try:
                           max_current_source  =doc.getElementsByTagName("Max_Current")
                           max_current_source = max_current_source[0].firstChild.nodeValue.encode('utf-8')
                           max_current_source = max_current_source.strip()
                       except:
                           max_current_source = None
                       print("||##################################||###############################||")
                       print("                                 New Source joined                       ")
                       print("  ipaddress                         || {}                             ".format(addr[0]))
                       print("  Source ID                         || {}                             ".format(id_source))
                       print("  Type                              || {}                             ".format(type_source))
                       print("  Source Value                      || {}                             ".format(value_source))
                       print("  Minimum Voltage                   || {}                             ".format(min_volt_source))
                       print("  Maximum Voltage                   || {}                             ".format(max_volt_source))
                       print("  Minimum Current                   || {}                             ".format(min_current_source))
                       print("  Maximum Current                   || {}                             ".format(max_current_source))
                       print("||##################################||###############################||")
                           
                       source = Source_struct(ip_address = addr[0] , id = id_load , type =type_load, value =value_load,min_volt = min_volt_source , max_volt = min_volt_source , min_curr = min_current_source, max_curr =min_current_source)
                       Source_list.append(source)
                       #print(Load_list)
                       #print("print load structure{}" .format(load))
                       #print("print laod structue value{}" .format(Load_list[0].value))
                   else:
                       pass                   
               ### to update a value of port
               elif tag_name.strip() == 'update':
                   print("It is update response")
                   verb = doc.getElementsByTagName("Noun")
                   verb = verb[0].firstChild.nodeValue.encode('utf-8')
                   if verb.strip() == 'Load':
                       id_load     = doc.getElementsByTagName("id")
                       id_load     = id_load[0].firstChild.nodeValue.encode('utf-8')
                       id_load     = id_load.strip()
                       type_load   = doc.getElementsByTagName("type")
                       type_load   = type_load[0].firstChild.nodeValue.encode('utf-8')
                       type_load   = type_load.strip()
                       value_load  = doc.getElementsByTagName("value")
                       value_load  = value_load[0].firstChild.nodeValue.encode('utf-8')
                       value_load  = value_load.strip()
                       try:
                           min_volt_load    = doc.getElementByTagName("Min_Voltage")
                           min_volt_load = min_volt_load[0].firstChild.nodeValue.encode('utf-8')
                           min_volt_load = min_volt_load.strip()
                       except:
                           min_volt_load = None
                       try:
                           max_volt_load    = doc.getElementsByTagName("Max_Voltage")
                           max_volt_load = max_volt_load[0].firstChild.nodeValue.encode('utf-8')
                           max_volt_load = max_volt_load.strip()
                       except:
                           max_volt_load = None
                       try:
                           min_current_load  = doc.getElementsByTagName("Min_Current")
                           min_current_load = min_current_load[0].firstChild.nodeValue.encode('utf-8')
                           min_current_load = min_current_load.strip()
                       except:
                           min_current_load = None
                       try:  
                           max_current_load  =doc.getElementsByTagName("Max_Current")
                           max_current_load = max_current_load[0].firstChild.nodeValue.encode('utf-8')
                           max_current_load = max_current_load.strip()
                       except:
                           max_current_load = None
                       for i in Load_list:
                           if id_load == i.id:
                               Load_list[Load_list.index(i)] = Load_struct(ip_address = addr[0] , id = id_load , type =type_load, value =value_load, min_volt = min_volt_load , max_volt = min_volt_load , min_curr = min_current_load, max_curr =min_current_load)
                               print("load list has been upated")
                               break
                           else:
                               pass
                          
                   elif verb.strip() == 'Source':
                       ### to get the element value of the load
                       id_source     = doc.getElementsByTagName("id")
                       id_source     = id_source[0].firstChild.nodeValue.encode('utf-8')
                       id_source     = id_source.strip()
                       type_source   = doc.getElementsByTagName("type")
                       type_source   = type_source[0].firstChild.nodeValue.encode('utf-8')
                       type_source   = type_source.strip()
                       value_source  = doc.getElementsByTagName("value")
                       value_source  = value_source[0].firstChild.nodeValue.encode('utf-8')
                       value_source  = value_source.strip()
                       try:
                           min_volt_source    = doc.getElementByTagName("Min_Voltage")
                           min_volt_source = min_volt_source[0].firstChild.nodeValue.encode('utf-8')
                           min_volt_source = min_volt_source.strip()
                       except:
                           min_volt_source = None
                       try:
                           max_volt_source    = doc.getElementsByTagName("Max_Voltage")
                           max_volt_source = max_volt_source[0].firstChild.nodeValue.encode('utf-8')
                           max_volt_source = max_volt_source.strip()
                       except:
                           max_volt_source = None
                       try:
                           min_current_source  = doc.getElementsByTagName("Min_Current")
                           min_current_source = min_current_source[0].firstChild.nodeValue.encode('utf-8')
                           min_current_source = min_current_source.strip()
                       except:
                           min_current_source = None
                       try:
                           max_current_source  =doc.getElementsByTagName("Max_Current")
                           max_current_source = max_current_source[0].firstChild.nodeValue.encode('utf-8')
                           max_current_source = max_current_source.strip()
                       except:
                           max_current_source = None
                       for i in Source_list:
                           if id_source == i.id:
                               Source_list[Source_list.index(i)] = Source_struct(ip_address = addr[0] , id = id_load , type =type_load, value =value_load,min_volt = min_volt_source , max_volt = min_volt_source , min_curr = min_current_source, max_curr =min_current_source)
                               print("Source list has been upated")
                               break
                           else:
                               pass
               else :
                    print("It is not a get response")
                    
               os.remove(receive_xml)
               message = None
               
           else:
                pass
               
               
               # Calls broadcast function to send message to all
#			message_to_send = "<" + addr[0] + "> " + message
#			message =message.strip()  #to remove the leading and  trailing spaces
#			message = message.lower() #to make the all the cases of message lower case it is for maching with the elements in tuple
#			"""We are checking wether the message is in the tuple or not if it is there we are send the command to the other beagle bone to do apporpriate action"""
#			if message in tup:	
#				print("{} in tuple".format(message))
#				comm_link(message,conn)
#			elif message in tup_ack:
#				pass
#			else:
#				conn.send(b'Invalidcommand')
#			
#			#broadcast(message_to_send, conn) 
#
#			"""message may have no content if the connection
#			is broken, in this case we remove the connection"""
#			# remove(conn)
#			#pass

              
if __name__ == "__main__":

  client =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
  t1=threading.Thread(target=Poll,args=())
  t1.start()
  admin ="admin"  # user name of switch
  Host = "192.168.0.10" #ip address of the switch
  Mac   =  namedtuple("Mac_Table" , "mac port_no ip_address") # required attibute for the mac table of the switch 
  Mac_Table=[]  #Mac table for storing the value of mac address and it's corresponding
  ip_addr,netmask = network.initial_conf() # get the ip address and the netmask for the system
  network.ARP_ping(ip_addr) #do arp ping to get the ip address and the mac address of all the system in the network
  telnet.telnet_update(Host,admin,ip_addr)  #to get the mac addresses of all the loads connected to switch 
  print("We are in main code")
  start_conn()
  while True:
          message = sys.stdin.readline()
          if message.strip() == "exit":
              sys.exit()
          else:
              message =None
  