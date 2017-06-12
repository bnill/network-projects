BEGIN {
#Initialize the variables for TCP1
num_bytes_1 = 0;

#Initialize the variables for TCP2
num_bytes_2 = 0;
}

{
  EVE = $1; TIME = $2; SOURCE = $3; DEST = $4; TYPE = $5; SIZE = $6; SOURCE_ADDR = $9; DEST_ADDR = $10;

#TCPA
if (EVE == "r" && TYPE == "tcp" && SOURCE == 2 && DEST == 3) {
	if(SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0"){
        	num_bytes_1 += SIZE - 20; 
	}
}

#TCPB
if (EVE == "r" && TYPE == "tcp" && SOURCE == 2 && DEST == 5) {
	if(SOURCE_ADDR =="4.0" && DEST_ADDR == "5.0"){
        	num_bytes_2 += SIZE - 20;
	}
}

}

END {

#Throughput varies competition starts and end time

#TCP1
throughput_1 = num_bytes_1/((40 - 5) * 1024) * 8
printf (throughput_1 "\n");

#TCP2
throughput_2 = num_bytes_2/((40 - 5) * 1024) * 8
printf (throughput_2 "\n");

}
