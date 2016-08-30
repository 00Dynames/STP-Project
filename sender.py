#!/usr/bin/python

import socket, sys, time, message, random

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender_socket.settimeout(1)

sender_args = {"reciever_ip":str(sys.argv[1]),
			   "reciever_port":int(sys.argv[2]),
               "file":str(sys.argv[3]),
               "MWS":int(sys.argv[4]),
               "MSS":int(sys.argv[5]),
               "timeout":str(sys.argv[6]),
               "pdrop":str(sys.argv[7]),
               "seed":str(sys.argv[8])
              }

dest = (sender_args["reciever_ip"], sender_args["reciever_port"])
reciever = {"connected":False, "IP":sender_args["reciever_ip"], "port":sender_args["reciever_port"]}
random.seed(sender_args["seed"])

#RTT = []

"""
Make connection -> handshake
TODO -> randomly choose initial sequence number (isn)
"""

while not reciever["connected"]:

	mess = message.Message([sender_args["reciever_port"], 0, 0, "", "SYN"])
	print mess.segment()

	try:
		sender_socket.sendto(mess.segment(), dest)
		data, server = sender_socket.recvfrom(reciever["port"])
	
		mess.parse_segment(data) 
		
		if mess.response["ACK"]:
			print mess.segment()
			reciever["connected"] = True
			mess = message.Message([reciever["port"], 0, 0, "", "SYN", "ACK"])
			sender_socket.sendto(mess.segment(), (reciever["IP"], reciever["port"]))
	
	except socket.timeout:
		pass


"""
Send file
"""

f = open(sender_args["file"], "r")
window = {"start":0, "end":0}
file_size = len(f.read())
f.seek(0)

while True:

	#print f.read(sender_args["MSS"]), random.random()
 	print f.tell()


	mess = message.Message([reciever["port"], 0, 0, f.read(sender_args["MSS"])])

	try:
		start = time.time()
		sender_socket.sendto(mess.segment(), dest)
		
		data, server = sender_socket.recvfrom(dest[1])

		#while not data:
		#	data, server = sender_socket.recvfrom(dest[1])



		end = time.time()
		#RTT.append((end - start) * 1000)    
		mess.parse_segment(data)
		print mess.segment()
		#print "[" +data + "] -> "+ "RTT = " + str(int((end - start) * 1000)) + "ms"
		
		
		time.sleep(1 - (time.time() - start))
		if f.tell() == file_size:
			break

	except socket.timeout:
		print "timeout"

"""
Close connection
"""



f.close()
print "sent"
#print "RTT min/avg/max = {}/{}/{} ms".format(str(int(min(RTT))), str(int(sum(RTT)/len(RTT))), str(int(max(RTT)))) 
