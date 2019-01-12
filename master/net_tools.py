# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 15:59:05 2019

@author: ud
"""

import subprocess
import re

def netmask_value(netmask):
    if netmask == "255.255.255.255":
        return 32
    elif netmask =="255.255.255.0":
        return 24
    elif netmask =="255.255.0.0":
        return 16
    elif netmask == "255.0.0.0":
        return 8
    else:
        return 0

def initial_conf():
    process_ip_address = subprocess.Popen("ifconfig |grep \"inet addr\"|awk -F\"[ :]+\" 'NR==1{print $4 \":\" $8}' ", shell =True, stdout =subprocess.PIPE)
    try:
        outs, errs = process_ip_address.communicate()
        ip_address,netmask =outs.split(':')
        ip_address =ip_address.strip()
        netmask = netmask.strip()
        #print (ip_address.strip())
        #print(netmask.strip())
        netmask =netmask_value(netmask.strip())
        #print (str(netmask)+"--netmask")
    except:
            process_ip_address.kill()
            outs, errs = process_ip_address.communicate()
            print(errs)
    return ip_address,netmask
    
def nmap(ip_address,netmask):
    process_nmap = subprocess.Popen("nmap"+"\t"+ "-sP"+ "\t" +ip_address+"/"+str(netmask), shell =True, stdout =subprocess.PIPE)
    try:
        outs, errs = process_nmap.communicate()
        print ("Nmap Process Completed")
    except:
            process_nmap.kill()
            outs, errs = process_nmap.communicate()
            print(errs)    
    #items_nmap = re.findall("Nmap scan report for.*$",outs,re.MULTILINE)
    #for p in items_nmap:
       # p = str(p)
       # p = p.split()
       # d = p[4].split('.')
        #if int(d[3]) != 1 and p[4] != "192.168.0.10":
         #   print(p[4])
def Arp(mac_address):
    process_arp_n = subprocess.Popen("arp -n|grep " +mac_address+"|awk '{print $1}'", shell =True, stdout =subprocess.PIPE)
    try:
        outs,errs =process_arp_n.communicate()
        print("Arp MAC process Completed")
        print(outs)
        return outs.strip()
    except:
        process_arp_n.kill()
        outs, errs = process_arp_n.communicate()
        print(errs) 


def ARP_ping(ip_address):
    process_arp_ping =subprocess.Popen("arping -I enp2s0 -c 2 "+ip_address, shell =True, stdout =subprocess.PIPE)   
    try:
        outs,errs =process_arp_ping.communicate()
        print("Arp ping Process Completed")
        print(outs)
        return outs.strip()
    except:
        process_arp_ping.kill()
        outs, errs = process_arp_ping.communicate()
        print(errs) 

        
def Self_Mac():
    process_self_mac =subprocess.Popen("ifconfig |grep HWaddr| awk 'NR==1{print $5}'", shell =True, stdout =subprocess.PIPE)  
    try:
        outs,errs =process_self_mac.communicate()
        print("Mac address obtained")
        outs=outs.strip()
        return outs
    except:
        process_self_mac.kill()
        outs, errs = process_self_mac.communicate()
        print(errs) 

#items_arp = re.findall("^.*ether.*$",outs,re.MULTILINE)
#print(items_arp)
#for p in items_arp:
#        p = str(p)
#        p =p.split()
#        ip_address =p[0]
#        mac_address= p[2]
#        print(ip_address+ "-------" +mac_address)