import socket, sys
from struct import *
import time
import random
from urlparse import urlparse #for validation of url

# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0
    size = len(msg)
    if(size % 2):
	size = size - 1
	s = ord(msg[size])
    # loop taking 2 characters at a time
    for i in range(0, size, 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w
     
    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);
     
    #complement and mask to 4 byte short
    s = ~s & 0xffff    
    return s

#start of packet
packet = '';
src_ip = ''
dst_ip = ''
#TCP_header
tcp_source_port = random.randint(2000, 65534)   # source port
tcp_dest_port = 80   # destination port

#last_receive_time
last_receive_time = time.time()

#cwnd initial values
current_cwnd = 1
max_cwnd = 1000

#ip_header construction
def create_ip_header(source_ip, dest_ip, data):
    ip_version = 4
    ip_ihl = 5
    ip_tos = 0 
    ip_tl = 20 + len(data) #total length, kernel will fill the correct length
    ip_id = random.randint(10000, 65534) #number of this packet
    ip_flags = 0
    ip_offset = 0
    ip_ttl = 255
    ip_protocol = socket.IPPROTO_TCP
    ip_checksum = 0 
    ip_destination = socket.inet_aton(dest_ip)
    ip_source = socket.inet_aton(source_ip)

    ver_ihl = (ip_version << 4) + ip_ihl
    ip_header = pack("!BBHHHBBH4s4s",
	             ver_ihl, ip_tos, ip_tl, ip_id, ip_offset, ip_ttl, ip_protocol, ip_checksum, ip_source, ip_destination)
    return ip_header

def create_tcp_header(source_ip, dest_ip, src_port, dest_port, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_psh, tcp_ack, data):
    tcp_offset = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
    tcp_rst = 0
    tcp_urg = 0
    tcp_reserved = 0
    tcp_window = socket.htons (5840)    #   maximum allowed window size
    tcp_checksum = 0
    tcp_urg_ptr = 0
 
    tcp_offset_res = (tcp_offset << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
 
    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH' , tcp_source_port, tcp_dest_port, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_checksum, tcp_urg_ptr)

    # pseudo header fields
    source_address = socket.inet_aton(source_ip)
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(data)
 
    psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
    psh = psh + tcp_header + data;
 
    tcp_check = checksum(psh)
    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = pack('!HHLLBBH' , tcp_source_port, tcp_dest_port, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('H' , tcp_check) + pack('!H' , tcp_urg_ptr)
    return tcp_header

def unpack_ip(packet):
    packet = packet[0] #convert packet to string
    ip_header_length = 20
    ip_header = packet[0:20]		
    iph = unpack("!BBHHHBBH4s4s", ip_header)
    ip_version = iph[0] >> 4				
    ip_tos = iph[1]					
    ip_tl = iph[2]					
    ip_id = iph[3]					
    ip_flags = iph[4] >> 13				
    ip_offset = iph[4] & 0x1FFF			
    ip_ttl = iph[5]					
    ip_protocol = iph[6]					
    ip_checksum = hex(iph[7])				
    ip_source = socket.inet_ntoa(iph[8])		
    ip_destination = socket.inet_ntoa(iph[9])
    if(checksum (ip_header) == ip_checksum):
		vali = 1
    else:
		vali = 0				
    ip_payload = packet[20:]			
    result = [ip_version, ip_header, ip_tos, ip_tl, ip_id, ip_flags, ip_offset, ip_ttl, ip_protocol, ip_checksum, ip_source, ip_destination, ip_payload]
    return result

def unpack_tcp(packet):
    packet = packet[0]
    packet = packet[20:]
    tcp_header_length = (ord(packet[12])>>4) * 4		
    tcph = unpack("!HHLLBBHHH", packet[:20])
    source_port = tcph[0] 					
    dst_port = tcph[1] 					
    seq = tcph[2] 					
    ack = tcph[3] 					
    data_off = tcph[4] >> 4
    flag_lib = {32, 16, 8, 4, 2, 1}				
    flag = tcph[5]
    flags = ""						
    for f in flag_lib:
		if tcph[5] & f:
			if f == 32:
				flags += "U"
			if f == 16:
				flags += "A"
			if f == 8:
				flags += "P"
			if f == 4:
				flags += "R"
			if f == 2:
				flags += "S"
			if f == 1:
				flags += "F"
    window = tcph[6] 					
    tcp_checksum = hex(tcph[7]) 				
    urgp = tcph[8] 					
    options = packet[20:tcp_header_length]			
    payload = packet[tcp_header_length:]		
    tcp_unpack = [source_port, dst_port, seq, ack, data_off, flags, window, tcp_checksum, urgp, payload]
    return tcp_unpack
    

def first_handshake(src_ip, dest_ip, src_port, dest_port):
    ip_header = create_ip_header(src_ip, dest_ip, '')
    tcp_header = create_tcp_header(src_ip, dest_ip, src_port, dest_port, 0, 0, 0, 1, 0, 0, '')
    packet = ip_header + tcp_header
    send_s.sendto(packet, (dest_ip, 0))
    sent_time = time.time()
    return sent_time

def receive_handshake_response(s_ip, d_ip, s_port, d_port, sent_time):
    global current_cwnd
    last_sent_time = sent_time
    while(1):
        second_handshake = recv_s.recvfrom(65535)
        if(second_handshake):
            ip_packet = unpack_ip(second_handshake)
			if(ip_packet[10] == d_ip):
				tcp_header = unpack_tcp(second_handshake)
				if(tcp_header[0] == 80 and tcp_header[1] == s_port):
					if('A' in tcp_header[5] and 'S' in tcp_header[5]):
						last_receive_time = time.time()
						current_cwnd += 1
						return tcp_header
			elif time.time() - last_receive_time > 180:
				print 'server not working'
				sys.exit()	
			elif time.time() - last_sent_time > 60:
				last_sent_time = first_handshake(s_ip, d_ip, s_port, d_port)
    
def third_handshake(src_ip, dest_ip, src_port, dest_port, seq, ack):
    ip_header = create_ip_header(src_ip, dest_ip, '')
    tcp_header = create_tcp_header(src_ip, dest_ip, src_port, dest_port, seq, ack, 0, 0, 0, 1, '')
    packet = ip_header + tcp_header
    send_s.sendto(packet, (dest_ip, 0))
    sent_time = time.time()
    return sent_time

def http_get_header(url, host):
    request = "GET "+url+" HTTP/1.0\nHost: "+host+"\nConnection: keep-alive\r\n\r\n"
    return request

def send_get_request(src_ip, dest_ip, src_port, dest_port, seq, ack, http):
    ip_header = create_ip_header(src_ip, dest_ip, '')
    tcp_header = create_tcp_header(src_ip, dest_ip, src_port, dest_port, seq, ack, 0, 0, 1, 1, http)
    packet = ip_header + tcp_header + http
    packet_length = len(packet)
    last_sent_time = time.time()
    send_s.sendto(packet, (dest_ip, 0))
    request_info = [packet_length, last_sent_time]
    return request_info

if len(sys.argv) == 2:
    try:
        send_s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error:
        print 'socket could not be created '
        sys.exit()

    try:
        recv_s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error:
        print 'socket could not be created '
        sys.exit()

	#creating socket to find source ip
    findipsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    url_link = sys.argv[1]
    if(url_link[len(url_link) - 1] == '/'):
        url_link = url_link[0 : len(url_link) - 1]
	
	check_url = urlparse(url_link)
    if ((check_url.scheme == "http") and (check_url.netloc != "")):
       pass
    else: 
       print "Url validation failed: Enter Correct URL link\n"
       sys.exit()
    
	#To find source ip, destination ip and assign a name for downloaded file
    downloadedfilename = ''

    #steps to decide the name of downloaded file 
    url_linksplithttp = url_link.split('http://')
    url_linksplitslash = url_linksplithttp[1].split('/')
    targetfile_index = len(url_linksplitslash)

    if url_linksplitslash[0] == url_linksplithttp[1] :
        #if only servername is given so index.html is decided as downloaded filename
        downloadedfilename = 'index.html' 
    else :
        #if entire complete link given, so last file with extension decided as downloaded file name
        downloadedfilename = url_linksplitslash[targetfile_index - 1] 

    #setting destination domain name server
    destination_servername = url_linksplitslash[0]
    findipsocket.connect((destination_servername, 0))
    #setting destination ip address
    destination_ipaddr = socket.gethostbyname(destination_servername)
    host = destination_ipaddr
    #setting source ip address
    source_ipaddr = findipsocket.getsockname()[0]
    src_ip = source_ipaddr
    dst_ip = destination_ipaddr

    #handshakes done for connection
    first_handshake_time = first_handshake(src_ip, dst_ip, tcp_source_port, tcp_dest_port)    
    second_handshake = receive_handshake_response(src_ip, dst_ip, tcp_source_port, tcp_dest_port, first_handshake_time)
    ackn = second_handshake[2] + 1
    seqn = second_handshake[3]
    last_sent_time = third_handshake(src_ip, dst_ip, tcp_source_port, tcp_dest_port, seqn, ackn)

    #start of http request HTTPGET
    http_header = http_get_header(url_link, host)

    #send HTTP_GET
    info = send_get_request(src_ip, dst_ip, tcp_source_port, tcp_dest_port, seqn, ackn, http_header)
    last_sent_time = info[1]
    ack_to_receive = seqn + len(http_header)
    seq_to_receive = ackn

    #receive HTTP
    result = ''
    initial_flag = 0
    error_flag = 0
    while(1):
        data = recv_s.recvfrom(65535)
        if(data):
            ip_info = unpack_ip(data)
			if(ip_info[10] == dst_ip and ip_info[11] == src_ip): #filtering the soucre and destination ip
				tcp_packet = ip_info[12]
                tcp_info = unpack_tcp(data)
				#cases on receiving the first TCP packet
				if(initial_flag == 0 and tcp_info[0] == tcp_dest_port and tcp_info[1] == tcp_source_port and tcp_info[2] == seq_to_receive and tcp_info[3] == ack_to_receive and 'F' not in tcp_info[5]): # filtering based on source and destn port , ack , seq and not Fin 
					if('HTTP/1.1 200 OK' in tcp_info[9]):
						current_cwnd += 1
						last_receive_time = time.time()
						result += tcp_info[9] #http payload
						initial_flag = 1
						ip_header = create_ip_header(src_ip, dst_ip, '')
						tcp_header = create_tcp_header(src_ip, dst_ip, tcp_source_port, tcp_dest_port, tcp_info[3], len(tcp_info[9]) + tcp_info[2], 0, 0, 0, 1, '')
						packet = ip_header + tcp_header + ''
						send_s.sendto(packet, (dst_ip, 0))
						ack_to_receive = tcp_info[3]
						seq_to_receive = tcp_info[2] + len(tcp_info[9])
						last_sent_packet = packet
						last_sent_time = time.time()
					if('HTTP/1.1 301' in tcp_info[9] or 'HTTP/1.1 302' in tcp_info[9] or 'HTTP/1.1 404' in tcp_info[9] or 'HTTP/1.1 500' in tcp_info[9]):
						error_flag = 1
						print 'Error occured: Expected status code 200 OK is not received !!'
						break
				if(initial_flag == 1 and tcp_info[0] == tcp_dest_port and tcp_info[1] == tcp_source_port and tcp_info[2] == seq_to_receive and tcp_info[3] == ack_to_receive and 'F' not in tcp_info[5]): # filtering based on source and destn port , ack , seq and not Fin
					if('HTTP/1.1 200 OK' in tcp_info[9]):
						if(current_cwnd + 1 <= max_cwnd):
							current_cwnd += 1
						else:
							current_cwnd = 1
						last_receive_time = time.time()
						result += tcp_info[9]
						ip_header = create_ip_header(src_ip, dst_ip, '')
						tcp_header = create_tcp_header(src_ip, dst_ip, tcp_source_port, tcp_dest_port, tcp_info[3], len(tcp_info[9]) + tcp_info[2], 0, 0, 0, 1, '')
						packet = ip_header + tcp_header + ''
						send_s.sendto(packet, (dst_ip, 0))
						ack_to_receive = tcp_info[3]
						seq_to_receive = tcp_info[2] + len(tcp_info[9])
						last_sent_packet = packet
						last_sent_time = time.time()
					if('HTTP/1.1 301' in tcp_info[9] or 'HTTP/1.1 302' in tcp_info[9] or 'HTTP/1.1 404' in tcp_info[9] or 'HTTP/1.1 500' in tcp_info[9]):
						error_flag = 1
						print 'Error occured: Expected status code 200 OK is not received !!'
						break
					#cases on TCP segment of a reassembled PDU
					elif(tcp_info[0] == tcp_dest_port and tcp_info[1] == tcp_source_port and tcp_info[2] == seq_to_receive and tcp_info[3] == ack_to_receive):
						if(current_cwnd + 1 <= max_cwnd):
							current_cwnd += 1
						else:
							current_cwnd = 1
						last_receive_time = time.time()
						ip_header = create_ip_header(src_ip, dst_ip, '')
						tcp_header = create_tcp_header(src_ip, dst_ip, tcp_source_port, tcp_dest_port, tcp_info[3], len(tcp_info[9]) + tcp_info[2], 0, 0, 0, 1, '')
						result += tcp_info[9]
						packet = ip_header + tcp_header + ''
						send_s.sendto(packet, (dst_ip, 0))
						ack_to_receive = tcp_info[3]
						seq_to_receive = tcp_info[2] + len(tcp_info[9])	
						last_sent_packet = packet
						last_sent_time = time.time()
				if(time.time() - last_receive_time > 60 and initial_flag == 0): # checking for timeout if we didnt http output at first instance
					send_get_request(src_ip, dst_ip, tcp_source_port, tcp_dest_port, seqn, ackn, http_header)
					last_sent_time = time.time()
					current_cwnd = 1
					continue
				if(time.time() - last_receive_time > 60 and initial_flag == 1): # checking for timeout if we didnt receive following TCP segments
					send_s.sendto(last_sent_packet, (dst_ip, 0))
					last_sent_time = time.time()
					current_cwnd = 1
					continue
				if(initial_flag == 1 and tcp_info[0] == tcp_dest_port and tcp_info[1] == tcp_source_port and tcp_info[2] == seq_to_receive and tcp_info[3] == ack_to_receive and 'F' in tcp_info[5]): #checking for last packet that contains F bit set
					#goodbye message
					if('P' in tcp_info[5]): #checking for new data 
						result += tcp_info[9]
					ip_header = create_ip_header(src_ip, dst_ip, '')
					tcp_header = create_tcp_header(src_ip, dst_ip, tcp_source_port, tcp_dest_port, tcp_info[3], tcp_info[2] + 1, 1, 0, 0, 1, '')
					packet = ip_header + tcp_header + ''
					send_s.sendto(packet, (dst_ip, 0))
					last_sent_time = time.time()
					last_sent_packet = packet
					break
				if(time.time() - last_receive_time > 180): #checking for data not received more than 3 minutes
					print 'Error: Connection failed because server has not responded'
					sys.exit()

    if(error_flag == 0):
        result = result.split('\r\n\r\n')[1]
        f = open(downloadedfilename , 'w')
        f.write(result)
        f.close()

    send_s.close()
    recv_s.close()

else:
    print "Invalid number of script arguments passed\n"
    sys.exit()
