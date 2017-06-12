BEGIN {
#Initialize the variables
# For Reno/Sack1
max_seq_TCP = 0;
max_ret_seq_TCP = 0;
pkt_cnt_TCP=0;
avg_delay_TCP=0;
total_delay_TCP=0;

# For CBR
max_seq_CBR = 0;
max_ret_seq_CBR = 0;
pkt_cnt_CBR=0;
avg_delay_CBR=0;
total_delay_CBR=0;

}

{
  EVE = $1; TIME = $2; SOURCE = $3; DEST = $4; TYPE = $5; SOURCE_ADDR = $9; DEST_ADDR = $10; SEQ = $11;

#TCP
#Record the largest SEQ when it is the currently last packet sent and record its starttime in the sending part of n1 and n2 in TCP flow
if (EVE == "-" && (SEQ >= max_seq_TCP) && TYPE == "tcp") {
	if(SOURCE == 0 && DEST == 1 && SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0"){
		max_seq_TCP = SEQ;
		start_time_TCP[max_seq_TCP] = TIME;
	}
}
#Record the largest RETURN SEQ and RECORD the return time to compute the latency
if (EVE == "r" && (SEQ >= max_ret_seq_TCP) && TYPE == "tcp") {
	if(SOURCE == 2 && DEST == 3 && SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0"){
		pkt_cnt_TCP += 1;
		max_ret_seq_TCP = SEQ
		end_time_TCP[max_ret_seq_TCP] = TIME;
		#calculate the delay when packet returns
		total_delay_TCP += end_time_TCP[max_ret_seq_TCP] - start_time_TCP[max_ret_seq_TCP];
	}
}

#CBR
#same with the process above
if (EVE == "-" && (SEQ >= max_seq_CBR) && TYPE == "cbr") {
	if(SOURCE == 4 && DEST == 1 && SOURCE_ADDR =="4.0" && DEST_ADDR == "5.0"){
		max_seq_CBR = SEQ;
		start_time_CBR[max_seq_CBR] = TIME;
	}
}

if (EVE == "r" && (SEQ >= max_ret_seq_CBR) && TYPE == "cbr") {
	if(SOURCE == 2 && DEST == 5 && SOURCE_ADDR =="4.0" && DEST_ADDR == "5.0"){
		pkt_cnt_CBR += 1;
		max_ret_seq_CBR = SEQ
		end_time_CBR[max_ret_seq_CBR] = TIME;
		total_delay_CBR += end_time_CBR[max_ret_seq_CBR] - start_time_CBR[max_ret_seq_CBR];
	}
}

}

END {

#Calculate Latency for TCP
if (pkt_cnt_T != "0") {
	avg_delay_TCP = total_delay_TCP/pkt_cnt_TCP;
printf ("avg_delay_tcp " avg_delay_TCP "\n");
}

#Calculate Latency for CBR
if (pkt_cnt_CBR != "0") {
	avg_delay_CBR = total_delay_CBR/pkt_cnt_CBR;
printf ("avg_delay_CBR " avg_delay_CBR "\n");
}

}
