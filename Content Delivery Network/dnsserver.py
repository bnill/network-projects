import sys
import os, struct, urllib, httplib2, socket, threading, time
from math import *

# preparing for server locations
# acquired from /course/cs5700f16/ec2-hosts.txt
servers_list = [
['ec2-54-210-1-206.compute-1.amazonaws.com', 'N. Virginia'],
['ec2-54-67-25-76.us-west-1.compute.amazonaws.com', 'N. California'],
['ec2-35-161-203-105.us-west-2.compute.amazonaws.com', 'Oregon'],
['ec2-52-213-13-179.eu-west-1.compute.amazonaws.com', 'Ireland'],
['ec2-52-196-161-198.ap-northeast-1.compute.amazonaws.com', 'Tokyo'],
['ec2-54-255-148-115.ap-southeast-1.compute.amazonaws.com', 'Singapore'],
['ec2-13-54-30-86.ap-southeast-2.compute.amazonaws.com', 'Sydney'],
['ec2-52-67-177-90.sa-east-1.compute.amazonaws.com', 'Sao Paolo'],
['ec2-35-156-54-135.eu-central-1.compute.amazonaws.com', 'Frankfurt']
]

server_ip_list = []
server_location_list = []
Radius = 6340
'''
for i in servers_list:
    server_ip_list.append(socket.gethostbyname(i[0]))
'''
#print server_ip_list


server_ip_list = ['54.210.1.206', '54.67.25.76', '35.161.203.105', '52.213.13.179', '52.196.161.198', '54.255.148.115', '13.54.30.86', '52.67.177.90', '35.156.54.135']

# longitude and latitude acquired from http://www.ipinfodb.com
# api_key
key = '3c11caba0f86dddde21e5601e0e9a265752fbc63f8bed5377e2796dd83dc79dd'
'''
for i in range(0, len(server_ip_list)):
    url = "http://api.ipinfodb.com/v3/ip-city/?key="+key+"&ip="+server_ip_list[i]
    content = urllib.urlopen(url).read()
    content = content.split(';')
    coordinate = []
    coordinate.append(content[2])
    coordinate.append(content[-3])
    coordinate.append(content[-2])
    #print coordinate
    end_time = time.time()
    server_location_list.append(coordinate)
    time.sleep(1.5)
    # not exceed the amount of requests per second

print server_location_list
'''
# this part of code is not included because the running time is high because of limit of requests in 1 second
server_location_list = [['54.210.1.206', '39.0437', '-77.4875'], ['54.67.25.76', '37.7749', '-122.419'], ['35.161.203.105', '47.6275', '-122.346'], ['52.213.13.179', '53.344', '-6.26719'], ['52.196.161.198', '35.6895', '139.692'], ['54.255.148.115', '1.28967', '103.85'], ['13.54.30.86', '47.6275', '-122.346'], ['52.67.177.90', '-23.5475', '-46.6361'], ['35.156.54.135', '47.6275', '-122.346']]

def find_client_location(c_ip):
    url = "http://api.ipinfodb.com/v3/ip-city/?key="+key+"&ip="+c_ip
    content = urllib.urlopen(url).read()
    content = content.split(';')
    coordinate = []
    coordinate.append(content[2])
    coordinate.append(content[-3])
    coordinate.append(content[-2])
    return coordinate

def server_ip_with_min_distance(coordinate, sl_list):
    distance = []
    for i in sl_list:
        distance.append(calculate_distance(float(coordinate[1]), float(coordinate[2]), float(i[1]), float(i[2])))
    #print distance
    min_distance = distance[0]
    min_index = 0
    for dist in distance:
        if(dist < min_distance):
            min_distance = dist
            min_index = distance.index(dist)
    return sl_list[min_index][0]

def calculate_distance(latitude1, longitude1, latitude2, longitude2):
    latitude1 = (pi/180.0) * latitude1  
    latitude2 = (pi/180.0) * latitude2  
    longitude1 = (pi/180.0) * longitude1  
    longitude2= (pi/180.0) * longitude2 
    #converting to float
    #calculate the spherical distance by formula
    tmp = cos(latitude1) * cos(latitude2) * cos(longitude2 - longitude1) + sin(latitude1) * sin(latitude2)
    distance_between = Radius * acos(tmp)
    return distance_between    

def send_answer_packet(t_id, question, server_ip, dest_ip, dest_port):
    packet = struct.pack("!H", t_id)
    packet += struct.pack("!H", 16 * 16 * 16 * 8) #0x8000
    packet += struct.pack("!H", 1)
    packet += struct.pack("!H", 1)
    packet += struct.pack("!H", 0)
    packet += struct.pack("!H", 0)
    tmp_question = question.split(".")
    for i in tmp_question:
        packet += struct.pack("!B", len(i))
        for j in bytes(i):
            packet += struct.pack("!c", j)
    packet += struct.pack("!B", 0)    # end of question
    packet += struct.pack("!H", 1)
    packet += struct.pack("!H", 1)
    packet += struct.pack("!H",49164) # pointer 0xC0C0
    packet += struct.pack("!H", 1)
    packet += struct.pack("!H", 1)
    packet += struct.pack("!I", 0)
    packet += struct.pack("!H", 4)
    tmp_ip = server_ip.split('.')
    for i in tmp_ip:
       packet += struct.pack("!B", int(i))
    sock.sendto(bytes(packet), (dest_ip, dest_port))

def dns_process(dns_request, c_ip, c_port, name, dnsserver_port):
    dns_unpack_result, t_id = dns_unpack(dns_request)
    #print dns_unpack_result
    #if(name != dns_unpack_result):
     #   print "error invalid question"
      #  sys.exit()
    #if already solved then return the cached server_ip
    if(client_ip_cache.has_key(c_ip)):
        return ip_cache[c_ip]
    #return the replica server with lowest RTT
    #return the client_ip from GeoIP
    coordinate = find_client_location(c_ip)
    closest_ip = server_ip_with_min_distance(coordinate, server_location_list)
    #print closest_ip
    send_answer_packet(t_id, dns_unpack_result, closest_ip, c_ip, c_port)

# return the question name of the DNS request
def dns_unpack(req):
    #header consists of 6 unsigned short (total 12 bytes)
    result = struct.unpack_from("!6H", req)
    transaction_id = result[0]  
    flags = result[1] #flags = 256 when it's a question request
    question_num = result[2]
    answer_RR = result[3]
    authority_RR = result[4]
    additional_RR = result[5]
    message = req[12:]
    # separate the type and class from query name (the last two unsigned short)
    unpack_type_class_result = struct.unpack('!HH', message[-4:])
    query_type = unpack_type_class_result[0]
    query_class = unpack_type_class_result[1]
    query_name = message[:-4]
    #transform the query name from ASCII
    i = 0
    query_name_tmp = []
    while 1:
        current_value = ord(query_name[i])
        if(current_value == 0):
            break
        i += 1
        index = current_value + i
        query_name_tmp.append(query_name[i: index])
        i = i + current_value
    dns_question = '.'.join(query_name_tmp)
    return dns_question, transaction_id
        
# python dnsserver.py -p 43210 -n cs5700cdn.example.com
# start of the dnsserver
host = ''
sys_input = sys.argv
port = sys_input[2]
name = sys_input[4]
client_ip_cache = dict() #this structure stores the client's best responsing replica server
max_number_of_request = 1000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, int(port)))
pthreads = []

while 1:
    dns_request, client_addr = sock.recvfrom(4096)
    client_ip = client_addr[0]
    client_port = client_addr[1]
    #print client_ip
    #print client_port
    t = threading.Thread(target = dns_process, args = (dns_request, client_ip, client_port, name, port))
    t.start()
    pthreads.append(t)
    
