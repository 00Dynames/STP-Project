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
              "csn": 0, # updated each time an ACK packet is received
              "status": 
                  {"data_transfered": 0,
                   "data_seg_sent": [],
                   "data_dropped": 0,
                   "data_delayed": 0,
                   "seg_retransmitted": 0,
                   "dup_acks": 0,
                   "acks": []
                  }
             }
    
    random.seed(sender["seed"]) # set seed
    sender["isn"] = int(random.random() * 13400) # 134 is random

    reciever = {"connected":False, 
                 "address":(sender["reciever_ip"], sender["reciever_port"]), # data is duplicated but makes more sense to group reciever data outside of the sender hash
                 "isn": 0
               }

    sender_pld = pld.Pld(sender["pdrop"])
    log_file = open("Sender_log.txt", "w+")
    timer_start = time.time()

    """
    Make connection -> handshake
    TODO -> randomly choose initial sequence number (isn)
    """

    while not reciever["connected"]:

        mess = message.Message([sender["reciever_port"], sender["isn"], 0, "", "SYN"])

        try:
            sender_socket.sendto(mess.segment(), reciever["address"]) # send SYN segment
            log_packet(log_file, mess, "snd", time.time() - timer_start)

            data, server = sender_socket.recvfrom(reciever["address"][1])
            mess.parse_segment(data) 

            if data: 
                log_packet(log_file, mess, "rcv", time.time() - timer_start) 
       
            if mess.response["ACK"] and mess.response["SYN"] and mess.ack_num == sender["isn"] + 1: # recieve SYN-ACK segment
                reciever["isn"] = mess.seq_num 
                sender["csn"] = mess.ack_num

                reciever["connected"] = True
                reciever["isn"] += 1
                mess = message.Message([reciever["address"][1], 0, reciever["isn"], "", "ACK"]) # send final ACK segment
                sender_socket.sendto(mess.segment(), reciever["address"])
                log_packet(log_file, mess, "snd", time.time() - timer_start)
    
        except socket.timeout:
            pass

    """
    Send file
    """
    window_file = open(sender["file"], "r")
    file_size = len(window_file.read())
    window_file.seek(0)

    window = {}

    while True:

        mess = message.Message([])

        try:
            window = make_window(window_file, file_size, sender, reciever)
            start = time.time()
            
            for packet in window:
                sent = sender_pld.send(sender_socket, window[packet], reciever)
                sender["status"]["data_transfered"] += len(window[packet].data)
                
                if not window[packet].seq_num in sender["status"]["data_seg_sent"]:
                    sender["status"]["data_seg_sent"].append(window[packet].seq_num)
                else:
                    sender["status"]["seg_retransmitted"] += 1

                if not sent:
                    log_packet(log_file, window[packet],"drop", time.time() - timer_start)
                    sender["status"]["data_dropped"] += 1
                else:
                    log_packet(log_file, window[packet], "snd", time.time() - timer_start)
         
            for i in range(len(window)):
                data, server = sender_socket.recvfrom(reciever["address"][1]) # recieve ack
                mess.parse_segment(data)
                log_packet(log_file, mess, "rcv", time.time() - timer_start)
        
                if not mess.ack_num in sender["status"]["acks"]:
                    sender["status"]["acks"].append(mess.ack_num)  
                else:
                    sender["status"]["dup_acks"] += 1

                if mess.response["ACK"] and mess.ack_num == sender["csn"] + sender["MSS"]:
                    sender["csn"] = mess.ack_num
        
            if window_file.tell() == file_size:
                break
            time.sleep(0.7)
        except socket.timeout:
          pass 

    """
    Close connection
    """

    fin_start = True

    while reciever["connected"]:
    
        try:
            if fin_start:
                mess = message.Message([reciever["address"][1], sender["csn"], reciever["isn"], "", "FIN"]) # send initial fin
                sender_socket.sendto(mess.segment(), reciever["address"]) # send initial fin
                log_packet(log_file, mess, "snd", time.time() - timer_start)

            data, server = sender_socket.recvfrom(reciever["address"][1])
            mess.parse_segment(data)
            log_packet(log_file, mess, "rcv", time.time() - timer_start)

            if mess.response["FIN"]: # recieve reciever fin
                mess.parse_segment("%s:%s:%s:%s:%s" % (reciever["address"][1], 0, reciever["isn"] + 1, "", "ACK"))
                sender_socket.sendto(mess.segment(), reciever["address"]) # send ack to reciever
                log_packet(log_file, mess, "snd", time.time() - timer_start)

                fin_start = False            
                time.sleep(2)
                reciever["connected"] = False
            elif mess.response["ACK"] and mess.ack_num == sender["csn"] + 1: # recieve initial ack
                fin_start = False

        except socket.timeout:
            pass

   
    window_file.close()

    log_file.write("\ndata transfered: %d, segments sent: %d, packet dropped: %d, segments retransmitted: %d, duplicate acks recieved: %d" % (sender["status"]["data_transfered"], len(sender["status"]["data_seg_sent"]), sender["status"]["data_dropped"], sender["status"]["seg_retransmitted"], sender["status"]["dup_acks"]))



"""
Write packet status to log file
"""
def log_packet(log_file, message, ptype, time):
    
    mtype = ""

    for res in message.response: # Check packet type          
        if message.response[res]:
            mtype += res[0]

    log_file.write("%s %.3f %s %d %d %d\n" % (ptype, time, mtype, message.seq_num, len(message.data), message.ack_num))

"""
Make a window of packets to send
"""
def make_window(text_file, file_size, sender, reciever): 

    window = {}
    window_size = 0
    window_csn = sender["csn"] 
    
    while window_size < sender["MWS"]:
        
        packet = message.Message([])
        text_file.seek(window_csn - sender["isn"] - 1) 

        packet.parse_segment("%s:%s:%s:%s:%s" % (reciever["address"][1], window_csn, reciever["isn"], text_file.read(sender["MSS"]), "ACK"))

        if window_size + len(packet.data) > sender["MWS"]: 
            break
        
        window[str(packet.seq_num)] = packet
        window_size += len(packet.data)
        window_csn += len(packet.data)
        if text_file.tell() == file_size:
            break

    return window

if __name__ == "__main__":
     main()
