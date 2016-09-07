"""
PLD Module
Class to simulate packet loss in demo env
"""

import socket, message, random

class Pld:

	def __init__(self, pdrop):
		self.pdrop = pdrop

	def send(self, socket, message, reciever):

		rand = random.random()
		print str(rand) + " ~ " + str(self.pdrop)

		if rand > self.pdrop:
			print "SENEEEEEDDD"
			socket.sendto(message.segment(), reciever["address"]) #: send SYN segment
			return True
		else:
			print "NOPE"
			return False

