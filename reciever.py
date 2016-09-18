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
                "buffer": {}
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

            print mess.segment() 

            if mess.response["ACK"] and sender["port"] != 0 and mess.ack_num == reciever["isn"] + 1:
                sender["connected"] = True
                reciever["isn"] += 1
                print "Connection made + ", sender["connected"]
                break
            elif mess.response["SYN"] and sender["port"] != 0: # syn segment sent when connected
                pass
            elif mess.response["SYN"] and sender["port"] == 0: # does not check ACK flag
                print "start connecting"
                sender["port"] = addr[1]
                sender["isn"] = mess.seq_num
                sender["csn"] = mess.seq_num + 1
                mess.parse_segment("%s:%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"], "", "ACK", "SYN"))  # no source port, SYN-ACK segment
                print mess.response["SYN"], mess.response["ACK"]
                reciever_socket.sendto(mess.segment(), addr)
                log_packet(log_file, mess, "snd", time.time() - timer_start)

        except socket.timeout:
            print "timeout"
     
    print "==> RECIEVE FILE <==="

    # scrape sender ip and/or port from UDP header

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
    
            #out_file.write(mess.data)
            
            reciever["buffer"][str(mess.seq_num)] = mess.data
            
            print mess.segment() 
            mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"] + len(mess.data), "", "ACK"))  # no source port, SYN-ACK segment
            reciever_socket.sendto(mess.segment(), addr)
            log_packet(log_file, mess, "snd", time.time() - timer_start)
            #print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
        except socket.timeout:
           print "timeout"

    print "===> CLOSING CONNECTION <==="
    print sender["connected"]
    """
    Close connection
    """

    while sender["connected"]:


        print "closing connection"

        try: # send reciever fin
            mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], 0, reciever["isn"], "", "FIN"))
            reciever_socket.sendto(mess.segment(), addr)
            log_packet(log_file, mess, "snd", time.time() - timer_start)
        
            data, addr = reciever_socket.recvfrom(2200)
            mess.parse_segment(data)
            log_packet(log_file, mess, "rcv", time.time() - timer_start)
                
            print reciever["isn"]
            if mess.response["ACK"] and mess.ack_num == reciever["isn"] + 1: # recieve ack
                print "CLOSE"
                sender["connected"] = False



        except socket.timeout:
            print "timeout"
     


    print "========"

    order = reciever["buffer"].keys()
    for i in range(len(order)):
        order[i] = int(order[i])

    order = sorted(order)
    print order
    
    for i in order:
        print i, reciever["buffer"][str(i)]


    reciever_socket.close()

    out_file.close()
    log_file.close()


def log_packet(log_file, message, ptype, time):

    mtype = ""
    for res in message.response: # Check packet type          
        if message.response[res]:
            mtype += res[0]
    
    log_file.write("%s %.3f %s %d %d %d\n" % (ptype, time, mtype, message.seq_num, len(message.data), message.ack_num))

if __name__ == "__main__":
    main() 
