#!/usr/bin/python

import socket, sys, time, message

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)

sender_args = {"reciever_ip":str(sys.argv[1]),
			   "reciever_port":int(sys.argv[2]),
               "file":str(sys.argv[3]),
               "MWS":str(sys.argv[4]),
               "MSS":str(sys.argv[5]),
               "timeout":str(sys.argv[6]),
               "pdrop":str(sys.argv[7]),
               "seed":str(sys.argv[8])
              }

host = socket.gethostbyname(socket.gethostname())
dest = (sender_args["reciever_ip"], sender_args["reciever_port"])
print host
reciever = {"connected":False}

#RTT = []

"""
Make connection -> handshake
TODO -> randomly choose initial sequence number (isn)
"""

while not reciever["connected"]:

	mess = message.Message([sender_args["reciever_port"], 0, 0, "", "SYN"])
	print mess.segment()
	print mess.parse_segment(mess.segment())

	try:
		sock.sendto(mess.segment(), dest)
		data, server = sock.recvfrom(dest[1])
	
		mess.parse_segment(data) 
		
		if mess.response["ACK"]:
			print mess.segment()
			reciever["connected"] = True
			mess = message.Message([sender_args["reciever_port"], 0, 0, "", "SYN", "ACK"])
			sock.sendto(mess.segment(), dest)
	
	except socket.timeout:
		pass


"""
Send file
"""

while True:
	try:
		start = time.time()
		sock.sendto("qwerew:QWERQWER:QWERQWER:QWERQWER:QWERQWER", dest)
		data, server = sock.recvfrom(dest[1])
		end = time.time()
		RTT.append((end - start) * 1000)    
		print "[" +data + "] -> "+ "RTT = " + str(int((end - start) * 1000)) + "ms"
		
		time.sleep(1 - (time.time() - start))


	except socket.timeout:
		pass

#print "RTT min/avg/max = {}/{}/{} ms".format(str(int(min(RTT))), str(int(sum(RTT)/len(RTT))), str(int(max(RTT)))) 
