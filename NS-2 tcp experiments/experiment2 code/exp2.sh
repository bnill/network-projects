#!/bin/bash

for CBR in $(seq 1000000 1000000 10000000)
#CBR starts from 1Mb to 10Mb step 1Mb
	do
		ns experiment2_start_same_RTT_same.tcl Reno Reno $CBR
		ns experiment2_start_same_RTT_same.tcl Newreno Reno $CBR
		ns experiment2_start_same_RTT_same.tcl Vegas Vegas $CBR
		ns experiment2_start_same_RTT_same.tcl Newreno Vegas $CBR

		gawk -f throughput.awk Reno-Reno-$CBR.tr >> reno_reno_throughput.csv
		gawk -f latency.awk Reno-Reno-$CBR.tr >> reno_reno_latency.csv
		gawk -f drop_rate.awk Reno-Reno-$CBR.tr >> reno_reno_drop_rate.csv

		gawk -f throughput.awk Newreno-Reno-$CBR.tr >> newreno_reno_throughput.csv
		gawk -f latency.awk Newreno-Reno-$CBR.tr >> newreno_reno_latency.csv
		gawk -f drop_rate.awk Newreno-Reno-$CBR.tr >> newreno_reno_drop_rate.csv


		gawk -f throughput.awk Vegas-Vegas-$CBR.tr >> vegas_vegas_throughput.csv
		gawk -f latency.awk Vegas-Vegas-$CBR.tr >> vegas_vegas_latency.csv
		gawk -f drop_rate.awk Vegas-Vegas-$CBR.tr >> vegas_vegas_drop_rate.csv


		gawk -f throughput.awk Newreno-Vegas-$CBR.tr >> newreno_vegas_throughput.csv
		gawk -f latency.awk Newreno-Vegas-$CBR.tr >> newreno_vegas_latency.csv
		gawk -f drop_rate.awk Newreno-Vegas-$CBR.tr >> newreno_vegas_drop_rate.csv

	done
