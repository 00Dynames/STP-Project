#!/usr/bin/python

import socket, sys, message
 
HOST = '127.0.0.1'
PORT = int(sys.argv[1])
sender = {"connected":False, "port":0}

try :
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((HOST, PORT))
	s.settimeout(1)
except socket.error , msg:
    print 'failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

"""
Listen for handshake
"""
while not sender["connected"]:

	try:
		data, addr = s.recvfrom(PORT)
	
		mess = message.Message([]) # Message(mess.parse_segment(data))
		mess.parse_segment(data)

		print mess.segment() 

		if mess.response["SYN"] and sender["port"] != 0 and addr[1] == sender["port"]:
			sender["connected"] == True
			print "Connection made"
			break
		elif mess.response["SYN"] and sender["port"] != 0:
			pass
		elif mess.response["SYN"] and sender["port"] == 0:
			sender["port"] = addr[1]
	    	mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], "0", "0", "", "ACK"))  # no source port
	    	s.sendto(mess.segment(), addr)
	except socket.timeout:
		print "timeout"
 
print "new loop"
# scrape sender ip and/or port from UDP header


while True:
	
	try:
		data, addr = s.recvfrom(2200)

		mess = message.Message([]) # Message(mess.parse_segment(data))
		mess.parse_segment(data)


		reply = 'OK...' + data
         
		mess.add_ack() 
		print mess.segment() 
		s.sendto(mess.segment(), addr)
		#print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
	except socket.timeout:
		print "timeout"

s.close()

