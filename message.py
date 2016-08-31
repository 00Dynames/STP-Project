"""
Message class to construct message strings 
	usage -> sock.sendto(message.string(), dest)

Parse incoming data strings into nice object format
	usage -> Message.parse((string) data)
"""
class Message:

	# content -> (source, dest, seqn, ackn, data, ack/syn/fin) <- required, ACK, SYN, FIN 
	def __init__(self, content):
		#source_port = content[0]
		if len(content) == 0:
			self.destination_port = 0
			self.seq_num = 0
			self.ack_num = 0
			self.data = ""
		else:		
			self.destination_port = content[0]
			self.seq_num = content[1]
			self.ack_num = content[2]
			self.data = content[3]

		self.response = {"ACK": False, "SYN": False, "FIN": False} # maybe able to work in as bits later in needed
	
		if "ACK" in content:	
			self.response["ACK"] = True
		if "SYN" in content:
			self.response["SYN"] = True
		if "FIN" in content:
			self.response["FIN"] = True

	def segment(self): # Format message data into string segment
		# segment structure -> source port:dest port:seq num:ack num:data:ACK:SYN:FIN
		data = "%s:%s:%s:%s" % (self.destination_port, self.seq_num, self.ack_num, self.data)
		
		# saf inserted in arbitrary order, must fix
		for item in self.response.keys():
			if item == "ACK" and self.response[item] == True:
				data += ":ACK"
			elif item == "SYN" and self.response[item] == True:
				data += ":SYN"
			elif item == "FIN" and self.response[item] == True:
				data += ":FIN"

		return data

	def parse_segment(self, in_data): # split incoming data string and pass to init function to set attributes
		data = str(in_data).split(":")
		self.__init__(data)
		
		return data

	def add_ack(self, num):
		self.response["ACK"] = True
		self.ack_num = num
