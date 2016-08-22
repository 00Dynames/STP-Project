import socket

#how to check if send is SYN/ACK/SYN-ACK

def pld_send(socket, message, dest):
	socket.sendto(message, dest)
