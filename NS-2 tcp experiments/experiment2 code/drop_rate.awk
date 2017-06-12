#DROP_RATE = (TOTAL_SEND - TOTAL_RECEIVE) / (TOTAL_SEND)
BEGIN {
#Initialize the variables for TCP1
pkt_sent_1=0;
pkt_recv_1=0;

#Initialize the variables for TCP2
pkt_sent_2=0;
pkt_recv_2=0; 
}

{
  EVE = $1; SOURCE = $3; DEST = $4; TYPE = $5; SOURCE_ADDR = $9; DEST_ADDR = $10;
#TCPA
#Calculate how many packets were sent and how many were received at the sink for TCP1

if (EVE == "+" && TYPE == "tcp" && SOURCE == 0 && DEST == 1) {
	if(SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0"){
		pkt_sent_1++;
	}
}

if (EVE == "r" && TYPE == "tcp" && SOURCE == 2 && DEST == 3) {
	if(SOURCE_ADDR == "0.0" && DEST_ADDR == "3.0"){
		pkt_recv_1++;
	}
}

#TCPB
#Calculate how many packets were sent and how many were received at the sink for TCP2

if (EVE == "+" && TYPE == "tcp" && SOURCE == 4 && DEST == 1) {
	if(SOURCE_ADDR =="4.0" && DEST_ADDR == "5.0"){
		pkt_sent_2++;
	}
}

if (EVE == "r" && TYPE == "tcp" && SOURCE == 2 && DEST == 5) {
	if(SOURCE_ADDR == "4.0" && DEST_ADDR == "5.0"){
		pkt_recv_2++;
	}
}

}

END {

#Calculate the drop rate for TCP A
if (pkt_sent_1 != "0") {
	printf (((pkt_sent_1 - pkt_recv_1)/pkt_sent_1) "\n");
}

#Calculate the drop rate for TCP B
if (pkt_sent_2 != "0") {
	printf (((pkt_sent_2 - pkt_recv_2)/(pkt_sent_2)) "\n");
}

}
