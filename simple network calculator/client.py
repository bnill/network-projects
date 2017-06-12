#!/usr/bin/python
import socket, sys, ssl

sarg_length = len(sys.argv)
socke = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if(sarg_length > 6):
    print "too many parameters!"
    exit()
if(sarg_length < 3):
    print "too few parameters!"
    exit()
elif (sarg_length == 6): 
    if (sys.argv[2].isdigit() == False) : #checking for port no. is integer
        print "Error: Port number entered is not integer value"
        exit ()
    port = int(sys.argv[2]);hostname = sys.argv[4]; NEU_ID = sys.argv[5]
    if(sys.argv[1] != "-p" or sys.argv[3] != "-s"): #checking for -p and -s options 
        print("Error: wrong parameter options provided")
        exit()
    elif (port > 65535): #checking for port no. correct range
        print "Error: port number is not in range 0-65535"
        exit()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_socke = context.wrap_socket(socke)
    try:
        ssl_socke.connect((hostname,port))
        ssl_flag = 1
    except:
        print "Error: Either of DNS name or IP address given is of wrong value"
        exit()
elif (sarg_length == 5): # -p alone
    if (sys.argv[2].isdigit() == False) :
        print "Error: Port number entered is not integer value"
        exit ()
    port = int(sys.argv[2]); hostname = sys.argv[3]; NEU_ID = sys.argv[4]
    if(sys.argv[1] != "-p"):
        print "Error: wrong parameter options provided"
        exit()
    elif (port > 65535):
        print "port number is not in range 0-65535"
        exit()
    try:
        socke.connect((hostname,port))
        ssl_flag = 0
    except:
        print "Error: Either of DNS name or ip address given is of wrong value"
        exit()
    
elif (sarg_length == 4): #-s alone
    if(sys.argv[1] != "-s"):
        print("Error: wrong parameter options provided")
        exit()
    port = 27994; hostname = sys.argv[2]; NEU_ID = sys.argv[3]
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_socke = context.wrap_socket(socke)
    try:
        ssl_socke.connect((hostname, port))
        ssl_flag = 1
    except:
        print "Error: Either of DNS name or ip address given is of wrong value"
        exit()
else : #only script name
    port = 27993; hostname = sys.argv[1]; NEU_ID = sys.argv[2]
    try:
        socke.connect((hostname,port))
        ssl_flag = 0
    except:
        print "Error: Either of DNS name or ip address given is of wrong value"
        exit()
              
def calculator(operand_1, operator, operand_2):
    if (operator == "+"):
        math_out = operand_1 + operand_2
        solution_message = "cs5700fall2016" + " " + str(math_out) + "\n"
    elif (operator == "-"):
        math_out = operand_1 - operand_2
        solution_message = "cs5700fall2016" + " " + str(math_out) + "\n"
    elif (operator == "*"):
        math_out = operand_1 * operand_2
        solution_message = "cs5700fall2016" + " " + str(math_out) + "\n"
    else:
        math_out = operand_1 / operand_2
        solution_message = "cs5700fall2016" + " " + str(math_out) + "\n"
    return solution_message

if (ssl_flag == 0) :
    hello_message = "cs5700fall2016 HELLO" + " " +str(NEU_ID)+ "\n"
    socke.send(hello_message)
    output = socke.recv(256)
    recv_out = output.split()
    math_out = 0;m_type = recv_out[1];f_operand = int(recv_out[2]);operator = recv_out[3];s_operand = int(recv_out[4])
    while m_type == "STATUS":
        s_message = calculator(f_operand, operator, s_operand)
        socke.send(s_message)
        output = socke.recv(256)
        recv_out = output.split()
        if recv_out[2] == "BYE" :
            if(recv_out[1] == "Unknown_Husky_ID"):
                print "Error: NEU_Husky_ID Provided is invalid"
                exit()            
            sec_key = recv_out[1]
            print sec_key
            break
        else :
            math_out = 0;m_type =  recv_out[1];f_operand = int(recv_out[2]);operator = recv_out[3];s_operand = int(recv_out[4])
else :
    hello_message = "cs5700fall2016 HELLO" + " " +str(NEU_ID)+ "\n"
    ssl_socke.send(hello_message)
    output = ssl_socke.recv(256)
    recv_out = output.split()
    math_out = 0;m_type =  recv_out[1];f_operand = int(recv_out[2]);operator = recv_out[3];s_operand = int(recv_out[4])
    while m_type == "STATUS":
        s_message = calculator(f_operand, operator, s_operand)
        ssl_socke.send(s_message)
        output = ssl_socke.recv(256)
        recv_out = output.split()
        if recv_out[2] == "BYE" :
            if(recv_out[1] == "Unknown_Husky_ID"):
                print "Error: NEU_Husky_ID Provided is invalid"
                exit()
            s_key = recv_out[1]
            print s_key
            break
        else :
            math_out = 0;m_type =  recv_out[1];f_operand = int(recv_out[2]);operator = recv_out[3];s_operand = int(recv_out[4])
    
