import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.7.1',2020))
print client_socket.recv(1024)
client_socket.close()
