#!/usr/bin/python

import socket, sys, message
 
HOST = '127.0.0.1'
PORT = int(sys.argv[1])
sender = {"connected":False, "port":0}

try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

"""
Listen for handshake
"""
while not sender["connected"]:
    
	data, addr = s.recvfrom(PORT)
	
	mess = message.Message([]) # Message(mess.parse_segment(data))
	mess.parse_segment(data)

	print mess.segment() 

	if mess.response["SYN"] and sender["port"] != 0 and addr[1] == sender["port"]:
		sender["connected"] == True
	elif mess.response["SYN"] and sender["port"] != 0:
		pass
	elif mess.response["SYN"] and sender["port"] == 0:
	    sender["port"] = addr[1]
	    mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], "0", "0", "", "ACK"))  # no source port
	    s.sendto(mess.segment(), addr)
 
print "new loop"

while True:
    
	data, addr = s.recvfrom(2200)
	
	mess = message.Message([]) # Message(mess.parse_segment(data))
	mess.parse_segment(data)
	print mess.segment() 


	if not data: 
		break
     
	reply = 'OK...' + data
     
	s.sendto(reply , addr)
	#print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
     
s.close()

