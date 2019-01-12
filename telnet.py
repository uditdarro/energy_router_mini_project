# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 15:32:30 2019

@author: ud
"""

# -*- coding: utf-8 -*-


import sys
import telnetlib
import re
from collections import namedtuple #used for making structure 
import sys
from astropy.table import Table
import threading
import net_tools as network


"""
Get the mac addresses of all the hosts connected to the switch and match with the mac table present in the main server. 
1) Get the mac address and ip address of the system 
2) Do the arp pingg in order to fill the mac table with all the ip addresses connected to the router
3) Match the ip addresses with the MAC address presented in the switch  and table of table of it .This is done so that ip address can be mapped to a physical port of a switch.
4) Keep updating the table of mac addresses and ip table so that if any port is removed or connected can be captured.
net_tools python file is created to use some of the network tools in the code
"""
def telnet_update(Host,admin,ip_addr):
        Mac_Table=[]  #Mac table for storing the value of mac address and it's corresponding
        Mac   =  namedtuple("Mac_Table" , "mac port_no ip_address") # required attibute for the mac table of the switch
        #initial_value = [0,0,None]
        initial_msg =None
    
        try:
            tn= telnetlib.Telnet(Host,23,5)
            print("Logged into telnet host")
            tn.write(admin+"\n")
        except:
            print("Not able to login into telnet host")
            sys.exit()
        try:
            tn.read_until("Password:")
            tn.write("admin"+"\n")
            tn.read_until("DGS-1210-10P> ")
            #print("password printed")
        except:
            print("Login or password error")
        try:
            tn.write("debug info"+"\n")
            x = tn.read_until("DGS-1210-10P> ")
            print(x)
            #tn.write("logout"+"\n")
            #tn.interact()
            #print(tn.read_all())
        except:
            print("Not able to get debug info")
            
        msg = re.findall("^.*Learnt.*$",x,re.MULTILINE)
        #   print(items)
        if initial_msg != msg :
            print("Mac Table getting updated ........")
            network.ARP_ping(ip_addr)
            Mac_Table=[]
            for p in msg:
                p=str(p)
                #print(p)
                a = p.split() # to split for multiple blank space convert p into string then split it without any parameter
                b = p.split('/') # to get the port number / is used as a splitter
                if a[1].strip() == network.Self_Mac(): # to get the self mac address and ip address as it is not avialable in arp table
                    mac_entry = Mac(mac =a[1].strip() ,port_no =int(b[1].strip()),ip_address=ip_addr)
                elif a[1].strip() == 'ac:84:c6:1f:3e:0d':
                    pass
                else:
                    try:
                        ip_entry =network.Arp(a[1].strip())
                    except:
                        ip_entry = None
                        print("IP not avialable")
                    mac_entry = Mac(mac =a[1].strip() ,port_no =int(b[1].strip()),ip_address=ip_entry)
#                if mac_entry not in Mac_Table:
#                #print("Not in mac table")
#                    print(mac_entry)
#                    for entry in Mac_Table:
#                        if mac_entry.mac == entry.mac:
#                            Mac_Table.remove(entry)    
#                            print( Mac_Table)
#                            sys.exit()
#                            break
#                        else:
#                            pass
                Mac_Table.append(mac_entry)
#                else:
#                    pass
            #print(a[1]+ "\t"+b[1])
            #print(Mac_Table)
        initial_msg =msg
        t1 = Table(rows =Mac_Table , names =('mac' ,'port no','ip address'))
        print(t1)

if __name__ == '__main__':     
    admin ="admin"  # user name of switch
    Host = "192.168.0.10" #ip address of the switch 
    ip_addr,netmask = network.initial_conf() # get the ip address and the netmask for the system
    network.ARP_ping(ip_addr) #do arp ping to get the ip address and the mac address of all the system in the network
    telnet_update()  #to get the mac addresses of all the loads connected to switch 