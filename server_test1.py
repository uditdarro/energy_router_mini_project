# Python program to implement server side of chat room.
import socket
import select
import sys 
import threading
import os



#######################################This section of code is regarding the setup of the server########################################
"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print ("Correct usage: script, IP address, port number")
    exit()
 
# takes the first argument from command prompt as IP address
IP_address = str(sys.argv[1])
 
# takes second argument from command prompt as port number
Port = int(sys.argv[2])
 
"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((IP_address, Port)) #this is to bind to an ip and  a port
 
"""
listens for 100 active connections. This number can be
increased as per convenience.
"""
server.listen(100)  #at most 100 clients can be connected to this server
#######################################################################################################################################


############This section of the code is regarding the maintaining the list of the clients and command dictionary aspect ##################

list_of_clients = []  #to create a list of client and to keep track of client of a client wether it is there or not
list_of_threads=[]  #to create a list of thread later to be deleted when not in use anymore
tup = ('connect' , 'disconnect' ,'energy', 'value','connect_req_ack','disconnect_req_ack')#to make  a list of commands which wil recived by the server
tup_ack =('invalidcommand','close_done','open_done')
dicton_echo = {'connect' : 'connect_ack' ,'disconnect':'disconnect_ack', 'time':'value','connect_req_ack':'close','disconnect_req_ack':'open'}#to make  a list of response which is given by the server to the connecting beagle bone
dicton_requ = {'connect': 'connect_req' , 'disconnect':'disconnect_req','connect_req_ack':'close','disconnect_req_ack':'open'}#This for the commands getting forwrd to the other port or PC

########################################################################################################################################

def clientthread(conn, addr):
 
    # sends a message to the client whose user object is conn
	conn.send(b"Welcome to this chatroom!")
 
	while True:
		print(threading.current_thread().name)
		try:
			message = conn.recv(4096)
			"""prints the message and address of the
			user who just sent the message on the server
			terminal"""
			message =message.decode('ASCII')
			print ("<" + addr[0] + "> " + message )
 			# Calls broadcast function to send message to all
			message_to_send = "<" + addr[0] + "> " + message
			message =message.strip()  #to remove the leading and  trailing spaces
			message = message.lower() #to make the all the cases of message lower case it is for maching with the elements in tuple
			"""We are checking wether the message is in the tuple or not if it is there we are send the command to the other beagle bone to do apporpriate action"""
			if message in tup:	
				print("{} in tuple".format(message))
				comm_link(message,conn)
			elif message in tup_ack:
				pass
			else:
				conn.send(b'Invalidcommand')
			
			#broadcast(message_to_send, conn) 

			"""message may have no content if the connection
			is broken, in this case we remove the connection"""
			# remove(conn)
			#pass
 
		except:
			continue
 
"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """
def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message.encode('ASCII'))
            except:
                clients.close()
 
                # if the link is broken, we remove the client
                remove(clients)
 

"""Using the you the appropriate reply  to the client again from the dictionary"""
def comm_link(message , conn):
	if len(list_of_clients) > 1:
		for clients in list_of_clients:
			if clients != conn:
				try:
					print("trying to execute comm_link function trying to send command to client1 and client2")
					print("Sending {} command to request".format(dicton_requ[message]))
					clients.send(dicton_requ[message].encode('ASCII')) #dicton_requ
					print("Sending {} command to echo".format(dicton_echo[message]))
					conn.send(dicton_echo[message].encode('ASCII')) #dicton_echo 
					print("Message send to client1 and client 2")
				except:
					client.close()
	else:
		conn.send(b"No one there to provide the energy sorry")

"""The following function simply removes the object
from the list that was created at the beginning of 
the program"""
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
 

def start_conn():
  while True:
 
    """Accepts a connection request and stores two parameters, 
    conn which is a socket object for that user, and addr 
    which contains the IP address of the client that just 
    connected"""
    conn, addr = server.accept()
 
    """Maintains a list of clients for ease of broadcasting
    a message to all available people in the chatroom"""
    list_of_clients.append(conn)
    print(list_of_clients)
    # prints the address of the user that just connected
    print (addr[0] + " connected")
 
    # creates and individual thread for every user 
    # that connects
    t1=threading.Thread(target=clientthread,args=(conn,addr,))    
    list_of_threads.append(t1)
    print(list_of_threads)
    t1.start()

#just to check the thread list later to be removed from code
def print_thread():
	print(list_of_threads)

def conn_close():
	for clients in list_of_clients:
		remove(clients)


if __name__ =='__main__':
	start_conn()
	t3=threading.Thread(traget= print_thread,args=())	
	t3.start()
	#this is to check wether the connected ip are alive or not 
	while True:
		for clients in list_of_clients:
			if os.system("ping -c 1 ", clients.addr[0]) == 0:
				pass
			else:
				remove(clients)
				print("The client address has been removed")
		
	conn_close()
	server.close()
