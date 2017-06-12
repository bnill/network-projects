BEGIN {
#monitor the latency between Node_(N1) and Node(N2)
#Average Latency = Sum of delay for all packets / total number of packets sent
avg_delay=0;
total_delay=0;
pkt_cnt=0;
}

{
  EVE = $1; TIME = $2; SOURCE = $3; DEST = $4; TYPE = $5; SOURCE_ADDR = $9; DEST_ADDR = $10; SEQ = $11;

if (EVE == "-" && TYPE == "tcp" && SOURCE == 0 && DEST == 1) {
	if(SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0"){
		start_time[SEQ] = TIME;
	}
}

#ack for receive
if (EVE == "r" && TYPE == "ack" && SOURCE == 1) {
	if(DEST == 0 && SOURCE_ADDR == "3.0" && DEST_ADDR == "0.0"){
		if (TIME > start_time[SEQ - 1]) {
			pkt_cnt++;
			latency = TIME - start_time[SEQ - 1];
			total_delay = latency + total_delay;
		}
	}  
}
}

END {

#Calculate Latency
if (pkt_cnt != "0") {
	avg_delay = total_delay/pkt_cnt;
printf (avg_delay "\n");
}

}
