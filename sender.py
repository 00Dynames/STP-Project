#!/usr/bin/python

import socket, sys, time, message, random, pld

def main():
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_socket.settimeout(1)
        
    sender = {"reciever_ip":str(sys.argv[1]),
              "reciever_port":int(sys.argv[2]),
              "file":str(sys.argv[3]),
              "MWS":int(sys.argv[4]),
              "MSS":int(sys.argv[5]),
              "timeout":str(sys.argv[6]),
              "pdrop":float(sys.argv[7]),
              "seed":str(sys.argv[8]),
              "isn": 0,
              "csn": 0
             }

    random.seed(sender["seed"])
    sender["isn"] = int(random.random() * 13400) # 134 is random

    reciever = {"connected":False, 
                 "address":(sender["reciever_ip"], sender["reciever_port"]),
                 "isn": 0
               }

    sender_pld = pld.Pld(sender["pdrop"])
    
    timer_start = time.time()

    out_file = open("Sender_log.txt", "w+")



    """
    Make connection -> handshake
    TODO -> randomly choose initial sequence number (isn)
    """

    while not reciever["connected"]:

        mess = message.Message([sender["reciever_port"], sender["isn"], 0, "", "SYN"])
        print mess.segment()

        try:
            sender_socket.sendto(mess.segment(), reciever["address"]) # send SYN segment
            log_packet(out_file, mess, "snd", time.time() - timer_start)

            data, server = sender_socket.recvfrom(reciever["address"][1])

            mess.parse_segment(data) 

            if data:
                log_packet(out_file, mess, "rcv", time.time() - timer_start) 


       
            if mess.response["ACK"] and mess.response["SYN"] and mess.ack_num == sender["isn"] + 1: # recieve SYN-ACK segment
                print "ACK:SYN", mess.segment()

                reciever["isn"] = mess.seq_num 
                sender["csn"] = mess.ack_num

                reciever["connected"] = True
                reciever["isn"] += 1
                mess = message.Message([reciever["address"][1], 0, reciever["isn"], "", "ACK"]) # send final ACK segment
                sender_socket.sendto(mess.segment(), reciever["address"])
                log_packet(out_file, mess, "snd", time.time() - timer_start)
    
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

        mess = message.Message([reciever["address"][1], sender["csn"], reciever["isn"], f.read(sender["MSS"]), "ACK"])

        try:
            start = time.time()
        
            #sender_socket.sendto(mess.segment(), reciever["address"])
            sent = sender_pld.send(sender_socket, mess, reciever) # send with pld module

            if not sent:
                log_packet(out_file, mess, "drop", time.time() - timer_start)
            else:
                log_packet(out_file, mess, "snd", time.time() - timer_start)

            data, server = sender_socket.recvfrom(reciever["address"][1])
            mess.parse_segment(data)
            log_packet(out_file, mess, "rcv", time.time() - timer_start)

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

    fin_start = True

    while reciever["connected"]:
    
        try:
            if fin_start:
                print "fin start"
                mess = message.Message([reciever["address"][1], sender["csn"], reciever["isn"], "", "FIN"]) # send initial fin
                sender_socket.sendto(mess.segment(), reciever["address"]) # send initial fin
                log_packet(out_file, mess, "snd", time.time() - timer_start)

            data, server = sender_socket.recvfrom(reciever["address"][1])
            mess.parse_segment(data)
            log_packet(out_file, mess, "rcv", time.time() - timer_start)

            if mess.response["FIN"]: # recieve reciever fin
                print "fin recieved"
                mess.parse_segment("%s:%s:%s:%s:%s" % (reciever["address"][1], 0, reciever["isn"] + 1, "", "ACK"))
                sender_socket.sendto(mess.segment(), reciever["address"]) # send ack to reciever
                log_packet(out_file, mess, "snd", time.time() - timer_start)

                fin_start = False            
                print reciever["isn"] + 1 
                time.sleep(2)
                reciever["connected"] = False
            elif mess.response["ACK"] and mess.ack_num == sender["csn"] + 1: # recieve initial ack
                print "fin success"
                fin_start = False

        except socket.timeout:
            pass
    




    f.close()
    print "sent"

"""
Write packet status to log file
"""
def log_packet(log_file, message, ptype, time):
    
    mtype = ""

    print "===" + str(message.response)

    for res in message.response: # Check packet type
               
        if message.response[res]:
            mtype += res[0]

    log_file.write("%s %.3f %s %d %d %d\n" % (ptype, time, mtype, message.seq_num, len(message.data), message.ack_num))

if __name__ == "__main__":
    main()
