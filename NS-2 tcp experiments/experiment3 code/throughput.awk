BEGIN {
}

{
  EVE = $1; TIME = $2; SOURCE = $3; DEST = $4; TYPE = $5; SIZE = $6; SOURCE_ADDR = $9; DEST_ADDR = $10;

#time of simulation 
for (t = 0; t < 90; t++) {

	if (EVE == "r" && TYPE == "tcp" && SOURCE == 2 && DEST == 3 && SOURCE_ADDR =="0.0" && DEST_ADDR == "3.0" && (TIME <= t+1) && (TIME > t)) {
		throughput_TCP[t] += ((SIZE - 20) * 8);
	}

	if (EVE == "r" && TYPE == "cbr" && SOURCE == 2 && DEST == 5 && SOURCE_ADDR =="4.0" && DEST_ADDR == "5.0" && (TIME <= t+1) && (TIME > t)) {
		throughput_CBR[t] += ((SIZE - 20) * 8);
	}
}

}

END {

for (t = 0; t < 90; t++) {
        printf("Throughput tcp from TIME %d to TIME %d = %.4f\n",t,t+1,(((throughput_TCP[t])/1024)/1024)/1);
        printf("Throughput cbr from TIME %d to TIME %d = %.4f\n",t,t+1,(((throughput_CBR[t])/1024)/1024)/1);
}

}
