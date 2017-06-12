lassign $argv TCP_SOURCE CBR_RATE QUEUE_LIMIT
#Create a simulator object
set ns [new Simulator]

#Open the ns trace file
set tf [open same_start-$TCP_SOURCE-$CBR_RATE-$QUEUE_LIMIT.tr w]
$ns trace-all $tf

#Define a finish procedure
proc finish {} {
        global ns tf
        $ns flush-trace
        close $tf
        exit 0
}

if { $TCP_SOURCE != "TCP" } {
	set TCP_SOURCE TCP/$TCP_SOURCE
}

#Create six nodes
set node_(N1) [$ns node]
set node_(N2) [$ns node]
set node_(N3) [$ns node]
set node_(N4) [$ns node]
set node_(N5) [$ns node]
set node_(N6) [$ns node]

#Create duplex links between the nodes
$ns duplex-link $node_(N1) $node_(N2) 10Mb 2ms DropTail
$ns duplex-link $node_(N2) $node_(N3) 10Mb 2ms DropTail
$ns duplex-link $node_(N3) $node_(N4) 10Mb 2ms DropTail
$ns duplex-link $node_(N5) $node_(N2) 10Mb 2ms DropTail
$ns duplex-link $node_(N3) $node_(N6) 10Mb 2ms DropTail

$ns queue-limit $node_(N1) $node_(N2) $QUEUE_LIMIT
$ns queue-limit $node_(N2) $node_(N3) $QUEUE_LIMIT
$ns queue-limit $node_(N3) $node_(N4) $QUEUE_LIMIT

#TCP Source at n1 and TCP Sink at n4
#change tcp types here
set tcp [new Agent/$TCP_SOURCE] 
$tcp set class_ 0
$tcp set window_ 5000
$ns attach-agent $node_(N1) $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $node_(N4) $sink
$ns connect $tcp $sink

#Setup a FTP Agent over the TCP connection or TCP won't be implemented
#according to the document
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

#udp used for cbr
set udp [new Agent/UDP]
$ns attach-agent $node_(N2) $udp
set null [new Agent/Null]
$ns attach-agent $node_(N3) $null
$ns connect $udp $null

#Setup a CBR over UDP connection
#Change CBR rate here
#set CBR_RATE 2Mb
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ $CBR_RATE
$cbr set random_ false

#Events for the CBR and TCP
$ns at 5.0 "$ftp start"
$ns at 40.0 "$ftp stop"
$ns at 5.0 "$cbr start"
$ns at 45.0 "$cbr stop"

$ns at 50.0 "finish"

#Run the simulation
$ns run
