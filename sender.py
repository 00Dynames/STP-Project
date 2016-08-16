#!/usr/bin/python
# specify python version later <- 2.7 as of 16/8

import sys, socket

socket = socket.socket()
sender_args = {}

#for arg in range(1, len(sys.argv)): #for now assume there will be 8 args

sender_args = {"reciever_ip":str(sys.argv[1]), 
			   "reciever_port":str(sys.argv[2]),
			   "file":str(sys.argv[3]),
			   "MWS":str(sys.argv[4]),
			   "MSS":str(sys.argv[5]),
			   "timeout":str(sys.argv[6]),
			   "pdrop":str(sys.argv[7]),
			   "seed":str(sys.argv[8])
			  }

print sender_args
