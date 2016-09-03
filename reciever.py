#!/usr/bin/python

import socket, sys, message, random
 
HOST = '127.0.0.1'
PORT = int(sys.argv[1])
sender = {"connected":False, "port":0, "isn": 0, "csn":0}
reciever = {"isn": int(random.random() * 100)}


"""
Bind socket
"""
try :
	reciever_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	reciever_socket.bind((HOST, PORT))
	reciever_socket.settimeout(1)
except socket.error , msg:
    print 'failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

"""
Listen for handshake
"""
while not sender["connected"]:

	try:
		data, addr = reciever_socket.recvfrom(PORT)
	
		mess = message.Message([]) 
		mess.parse_segment(data)

		print mess.segment() 

		if mess.response["ACK"] and sender["port"] != 0 and mess.ack_num == reciever["isn"] + 1:
			sender["connected"] == True
			print "Connection made"
			break
		elif mess.response["SYN"] and sender["port"] != 0: # syn segment sent when connected
			pass
		elif mess.response["SYN"] and sender["port"] == 0: # does not check ACK flag
			print "start connecting"
			sender["port"] = addr[1]
			sender["isn"] = mess.seq_num
			sender["csn"] = mess.seq_num + 1
	    	mess.parse_segment("%s:%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"], "", "ACK", "SYN"))  # no source port, SYN-ACK segment
	    	reciever_socket.sendto(mess.segment(), addr)

	except socket.timeout:
		print "timeout"
 
print "==> RECIEVE FILE <==="

# scrape sender ip and/or port from UDP header

"""
Recieve file
"""

while True:
	
	try:
		data, addr = reciever_socket.recvfrom(2200)

		mess.parse_segment(data)

		if mess.response["FIN"]:
			break
		sender["csn"] = mess.seq_num

		print mess.segment() 
		mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], 0, sender["csn"] + len(mess.data), "", "ACK"))  # no source port, SYN-ACK segment
		reciever_socket.sendto(mess.segment(), addr)
		#print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
	except socket.timeout:
		print "timeout"

print "===> CLOSING CONNECTION <==="

"""
Close connection
"""




reciever_socket.close()

