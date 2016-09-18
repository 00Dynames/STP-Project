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

		if rand > self.pdrop:
			socket.sendto(message.segment(), reciever["address"]) #: send ACK dataa segment
			return True
		else:
			return False

