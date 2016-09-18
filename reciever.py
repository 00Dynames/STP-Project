#!/usr/bin/python

import socket, sys, message, random, time
 
def main(): 
    
    sender = {"connected":False, "port":0, "isn": 0, "csn":0}
    reciever = {"IP": '127.0.0.1',
                "port": int(sys.argv[1]),
                "isn": int(random.random() * 10000), 
                "data_recieved": 0,
                "seg_recieved": 0,
                "dup_recieved": 0, 
                "buffer": {},
                "seg": []
               }

    out_file = open(sys.argv[2], "w+") 
    log_file = open("reciever_log.txt", "w+")

    timer_start = time.time()
    mess = message.Message([]) # Initialise message object

    """
    Bind socket
    """
    try :
        reciever_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        reciever_socket.bind((reciever["IP"], reciever["port"]))
        reciever_socket.settimeout(1)
    except socket.error , msg:
        print 'failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    """
    Connect to sender
    """
    while not sender["connected"]:

        try:
            data, addr = reciever_socket.recvfrom(reciever["port"])
            mess.parse_segment(data)

            if data:
                log_packet(log_file, mess, "rcv", time.time() - timer_start)

            if mess.response["ACK"] and sender["port"] != 0 and mess.ack_num == reciever["isn"] + 1:
                sender["connected"] = True
                reciever["isn"] += 1
                break
            elif mess.response["SYN"] and sender["port"] != 0: # syn segment sent when connected
                pass
            elif mess.response["SYN"] and sender["port"] == 0: # does not check ACK flag
                sender["port"] = addr[1]
                sender["isn"] = mess.seq_num
                sender["csn"] = mess.seq_num + 1
                mess.parse_segment("%s:%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"], "", "ACK", "SYN"))  # no source port, SYN-ACK segment
                reciever_socket.sendto(mess.segment(), addr)
                log_packet(log_file, mess, "snd", time.time() - timer_start)

        except socket.timeout:
            pass

    """
    Recieve file
    """

    while True:
    
        try:
            data, addr = reciever_socket.recvfrom(2200)

            mess.parse_segment(data)
            log_packet(log_file, mess, "rcv", time.time() - timer_start)
            
            
            sender["csn"] = mess.seq_num
            
            if mess.response["FIN"]: # acknowledge sender fin
                mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"] + 1, "", "ACK"))
                reciever_socket.sendto(mess.segment(), addr) # send ack
                log_packet(log_file, mess, "snd", time.time() - timer_start)
                break
    
            if str(mess.seq_num) not in reciever["buffer"].keys(): 
                reciever["buffer"][str(mess.seq_num)] = mess.data
            
            reciever["data_recieved"] += len(mess.data)
            reciever["seg_recieved"] += 1
            
            if not mess.seq_num in reciever["seg"]:
                reciever["seg"].append(mess.seq_num)
            else:
                reciever["dup_recieved"] += 1

            mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"] + len(mess.data), "", "ACK"))  # no source port, SYN-ACK segment
            reciever_socket.sendto(mess.segment(), addr)
            log_packet(log_file, mess, "snd", time.time() - timer_start)
        except socket.timeout:
           reciever_socket.sendto(mess.segment(), addr)
           log_packet(log_file, mess, "snd", time.time() - timer_start)

    """
    Close connection
    """

    while sender["connected"]:

        try: # send reciever fin
            mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], 0, reciever["isn"], "", "FIN"))
            reciever_socket.sendto(mess.segment(), addr)
            log_packet(log_file, mess, "snd", time.time() - timer_start)
        
            data, addr = reciever_socket.recvfrom(2200)
            mess.parse_segment(data)
            log_packet(log_file, mess, "rcv", time.time() - timer_start)
                
            if mess.response["ACK"] and mess.ack_num == reciever["isn"] + 1: # recieve ack
                sender["connected"] = False

        except socket.timeout:
            pass
     
    order = reciever["buffer"].keys()
    for i in range(len(order)):
        order[i] = int(order[i])

    order = sorted(order)
    
    for i in order:
        out_file.write(reciever["buffer"][str(i)])

    reciever_socket.close()
    out_file.close()
   
    log_file.write("\ndata recieved: %d, data segments recieved: %d, duplicate segments recieved: %d" % (reciever["data_recieved"], reciever["seg_recieved"], reciever["dup_recieved"]))
    log_file.close()
    
def log_packet(log_file, message, ptype, time):

    mtype = ""
    for res in message.response: # Check packet type          
        if message.response[res]:
            mtype += res[0]
    
    log_file.write("%s %.3f %s %d %d %d\n" % (ptype, time, mtype, message.seq_num, len(message.data), message.ack_num))

if __name__ == "__main__":
    main() 
