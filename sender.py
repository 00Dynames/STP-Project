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
               "seed":str(sys.argv[8]),
			   "isn": 0
		      }

random.seed(sender_args["seed"])
sender_args["isn"] = int(random.random() * 134) # 134 is random

reciever = {"connected":False, 
  	        "address":(sender_args["reciever_ip"], sender_args["reciever_port"]),
  			"isn": 0
		   }

"""
Make connection -> handshake
TODO -> randomly choose initial sequence number (isn)
"""

while not reciever["connected"]:

	mess = message.Message([sender_args["reciever_port"], sender_args["isn"], 0, "", "SYN"])
	print mess.segment()

	try:
		sender_socket.sendto(mess.segment(), reciever["address"]) # send SYN segment
		data, server = sender_socket.recvfrom(reciever["address"][1])
	
		mess.parse_segment(data) 
		
		if mess.response["ACK"] and mess.response["SYN"] and mess.ack_num == sender_args["isn"]: # recieve SYN-ACK segment
			print mess.segment()

			reciever["isn"] = mess.seq_num

			reciever["connected"] = True
			mess = message.Message([reciever["address"][1], 0, reciever["isn"] + 1, "", "ACK"]) # send final ACK segment
			sender_socket.sendto(mess.segment(), reciever["address"])
	
	except socket.timeout:
		pass


"""
Send file
"""

f = open(sender_args["file"], "r")
window = {"start":0, "end":0}
file_size = len(f.read())
f.seek(0)

isn = int(random.random() * 100)

while True:

	#print f.read(sender_args["MSS"]), random.random()
 	print f.tell()

	mess = message.Message([reciever["address"][1], isn + sender_args["MSS"], 0, f.read(sender_args["MSS"])])

	try:
		start = time.time()
		sender_socket.sendto(mess.segment(), reciever["address"])
		
		data, server = sender_socket.recvfrom(reciever["address"][1])

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

while reciever["connected"]:
	

	try:
		mess = message.Message([reciever["address"][1], 0, 0,"", "FIN"])
		sender_socket.sendto(mess.segment(), reciever["address"])

		data, server = sender_socket.recvfrom(reciever["address"][1])
		
		mess.parse_segment(data)

		if mess.responses["FIN"]:
			print "FIN!!!!"
		else:
			pass

	except socket.timeout:
		pass
	
	print "fin"



f.close()
print "sent"
#print "RTT min/avg/max = {}/{}/{} ms".format(str(int(min(RTT))), str(int(sum(RTT)/len(RTT))), str(int(max(RTT)))) 
