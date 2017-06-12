BEGIN {
#Initialize the variables for TCP1
avg_delay_1=0;
total_delay_1=0;
pkt_cnt_1=0;

#Initialize the variables for TCP2
avg_delay_2=0;
total_delay_2=0;
pkt_cnt_2=0;
}

{
  EVE = $1; TIME = $2; SOURCE = $3; DEST = $4; TYPE = $5; SOURCE_ADDR = $9; DEST_ADDR = $10; SEQ = $11;

#TCP1
#TIME for sent packet
if (EVE == "-" && TYPE == "tcp" && SOURCE == 0 && DEST == 1) {
	if(SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0"){
		start_time_1[SEQ] = TIME;
	}
}

#TIME for the ACK packet in TCP
if (EVE == "r" && TYPE == "ack" && SOURCE == 1 && DEST == 0) {
	if( SOURCE_ADDR == "3.0" && DEST_ADDR == "0.0"){
		if (TIME > start_time_1[SEQ - 1]) {
			pkt_cnt_1 += 1;
			latency_1 = TIME - start_time_1[SEQ - 1];
			total_delay_1 += latency_1;
		}
	}  
}

#TCP2
if (EVE == "-" && TYPE == "tcp" && SOURCE == 4 && DEST == 1) {
	if(SOURCE_ADDR =="4.0" && DEST_ADDR == "5.0"){
		start_time_2[SEQ] = TIME;
	}
}

if (EVE == "r" && TYPE == "ack" && SOURCE == 1 && DEST == 4) {
	if(SOURCE_ADDR == "5.0" && DEST_ADDR == "4.0"){
		if (TIME > start_time_2[SEQ - 1]) {
			pkt_cnt_2 += 1;
			latency_2 = TIME - start_time_2[SEQ - 1];
			total_delay_2 += latency_2;
		}
	}  
}

}

END {

#Calculate Latency for TCP Source A
if (pkt_cnt_1 != "0") {
	avg_delay_1 = total_delay_1/pkt_cnt_1;
	printf (avg_delay_1 "\n");
}

#Calculate Latency for TCP Source B
if (pkt_cnt_2 != "0") {
	avg_delay_2 = total_delay_2/pkt_cnt_2;
	printf (avg_delay_2 "\n");
}

}
