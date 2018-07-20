import socket
import threading

bind_ip ="10.114.56.122"
bind_port = 2020
server =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((bind_ip,bind_port))
server.listen(5)
print("[+] Listening on",bind_ip,bind_port)

def handle_client(client_socket):
	request =client_socket.recv(1024)
	print("[+] client:",request)
	client_socket.send(b"[!] we have encountered a problem....")
	client_socket.close()
def Message_client(client_socket,address):
	while True:
		request =client_socket.recv(1024)
		print("@",address,">>:",request)
		client_socket.send(message.encode('ASCII'))

while True:	
	client,addr= server.accept()
	print ("[+] Accepting connection from:",addr[0],addr[1])
	print ("[+] Establishing connection from:",addr[0],addr[1])
	client.send(b'you are connected to server')
	client_handler =threading.Thread(target=handle_client,args=(client,))
	Message_handler=threading.Thread(target=Message_client,args=(client,addr[0],))
	client_handler.start()
	Message_handler.start()
