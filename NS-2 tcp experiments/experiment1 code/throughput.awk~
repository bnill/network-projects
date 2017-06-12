BEGIN {
#Monitor the throughput between Node_(N3) and Node(N4)
num_bytes = 0;
}

{
  EVE = $1; SOURCE = $3; DEST = $4; TYPE = $5; SIZE = $6; SOURCE_ADDR = $9; DEST_ADDR = $10;

if (EVE == "r" && TYPE == "tcp" && SOURCE == 2 && DEST == 3) {
	if(SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0"){
        	num_bytes += SIZE - 20;
	}
}

}

END {

#Throughput varies wrt start and end time set
throughput = num_bytes/((40 - 5) * 1024) * 8
printf (throughput " Kbps" "\n");
}
