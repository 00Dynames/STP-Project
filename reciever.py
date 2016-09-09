#!/usr/bin/python

import socket, sys, message, random
 
def main(): 
    HOST = '127.0.0.1'
    PORT = int(sys.argv[1])
    sender = {"connected":False, "port":0, "isn": 0, "csn":0}
    reciever = {"isn": int(random.random() * 10000)}

    out = open("test_out.txt", "w+") 

    """
    Bind socket
    """
    try :
        reciever_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        reciever_socket.bind((HOST, PORT))
        reciever_socket.settimeout(1)
    except socket.error , msg:
        print 'failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    """
    
    """
    while not sender["connected"]:

        try:
            data, addr = reciever_socket.recvfrom(PORT)
    
            mess = message.Message([]) 
            mess.parse_segment(data)

            print mess.segment() 

            if mess.response["ACK"] and sender["port"] != 0 and mess.ack_num == reciever["isn"] + 1:
                sender["connected"] = True
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
            sender["csn"] = mess.seq_num

            if mess.response["FIN"]: # acknowledge sender fin
                mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"] + 1, "", "ACK"))
                reciever_socket.sendto(mess.segment(), addr) # send ack
                break
    
            out.write(mess.data)
            print mess.segment() 
            mess.parse_segment("%s:%s:%s:%s:%s" % (sender["port"], reciever["isn"], sender["csn"] + len(mess.data), "", "ACK"))  # no source port, SYN-ACK segment
            reciever_socket.sendto(mess.segment(), addr)
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
        
            data, addr = reciever_socket.recvfrom(2200)
            mess.parse_segment(data)

            print reciever["isn"]
            if mess.response["ACK"] and mess.ack_num == reciever["isn"] + 2: # recieve ack
                print "CLOSE"
                sender["connected"] = False



        except socket.timeout:
            print "timeout"
     




    reciever_socket.close()

    out.close()

if __name__ == "__main__":
    main()
