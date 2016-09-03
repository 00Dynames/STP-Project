#!/usr/bin/python

import socket, sys, time, message, random

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender_socket.settimeout(1)

sender = {"reciever_ip":str(sys.argv[1]),
			   "reciever_port":int(sys.argv[2]),
               "file":str(sys.argv[3]),
               "MWS":int(sys.argv[4]),
               "MSS":int(sys.argv[5]),
               "timeout":str(sys.argv[6]),
               "pdrop":str(sys.argv[7]),
               "seed":str(sys.argv[8]),
			   "isn": 0,
			   "csn": 0

		      }

random.seed(sender["seed"])
sender["isn"] = int(random.random() * 134) # 134 is random

reciever = {"connected":False, 
  	        "address":(sender["reciever_ip"], sender["reciever_port"]),
  			"isn": 0
		   }

"""
Make connection -> handshake
TODO -> randomly choose initial sequence number (isn)
"""

while not reciever["connected"]:

	mess = message.Message([sender["reciever_port"], sender["isn"], 0, "", "SYN"])
	print mess.segment()

	try:
		sender_socket.sendto(mess.segment(), reciever["address"]) # send SYN segment
		data, server = sender_socket.recvfrom(reciever["address"][1])
	
		mess.parse_segment(data) 
		
		if mess.response["ACK"] and mess.response["SYN"] and mess.ack_num == sender["isn"] + 1: # recieve SYN-ACK segment
			print "ACK:SYN", mess.segment()

			reciever["isn"] = mess.seq_num 
			sender["csn"] = mess.ack_num

			reciever["connected"] = True
			mess = message.Message([reciever["address"][1], 0, reciever["isn"] + 1, "", "ACK"]) # send final ACK segment
			sender_socket.sendto(mess.segment(), reciever["address"])
	
	except socket.timeout:
		pass

if sender["csn"] - sender["isn"] == 1:
	print "===> SEND FILE <==="



"""
Send file
"""

f = open(sender["file"], "r")
window = {"start":0, "end":0}
file_size = len(f.read())
f.seek(0)



while True:

	#print f.read(sender["MSS"]), random.random()
 	print f.tell()

	f.seek(sender["csn"] - sender["isn"] - 1) # seek to position given by last seq_num

	mess = message.Message([reciever["address"][1], sender["csn"], 0, f.read(sender["MSS"])])

	try:
		start = time.time()
		sender_socket.sendto(mess.segment(), reciever["address"])
		
		data, server = sender_socket.recvfrom(reciever["address"][1])

		end = time.time()
		#RTT.append((end - start) * 1000)    
		mess.parse_segment(data)
		print mess.segment()
		
		if mess.response["ACK"] and mess.ack_num == sender["csn"] + sender["MSS"]:
			sender["csn"] = mess.ack_num


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
