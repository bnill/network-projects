#!/bin/bash
ns tcp-queuing.tcl Reno DropTail
ns tcp-queuing.tcl Reno RED
ns tcp-queuing.tcl Sack1 RED

gawk -f throughput.awk Reno-DropTail.tr >> reno_droptail_throughput_cbr_first.csv
gawk -f latency.awk Reno-DropTail.tr >> reno_droptail_latency_cbr_first.csv

gawk -f throughput.awk Reno-RED.tr >> reno_red_throughput_cbr_first.csv
gawk -f latency.awk Reno-RED.tr >> reno_red_latency_cbr_first.csv

ns tcp-queuing.tcl Sack1 DropTail
gawk -f throughput.awk Sack1-DropTail.tr >> sack_droptail_throughput_cbr_first.csv
gawk -f latency.awk Sack1-DropTail.tr >> sack_droptail_latency_cbr_first.csv

gawk -f throughput.awk Sack1-RED.tr >> sack_red_throughput_cbr_first.csv
gawk -f latency.awk Sack1-RED.tr >> sack_red_latency_cbr_first.csv
